from .base import TrackProvider
import arrow
import gnupg
import logging
import math
from datetime import datetime, timedelta, time
from django.utils.timezone import utc
from django.contrib.gis.geos import Point
from sport.models import Sport
from tracks.models import TrackSplit
from garmin_uploader.user import User as GarminUser

logger = logging.getLogger('runreport.sport.garmin')


class GarminAuthException(Exception):
    '''
    Used when the specific garmin login process fails
    '''
    pass


class GarminProvider(TrackProvider):
    NAME = 'garmin'
    settings = ['GPG_HOME', 'GPG_PASSPHRASE', ]

    # Data Urls
    url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'
    url_laps = 'https://connect.garmin.com/proxy/activity-service/activity/%s/splits'
    url_polyline = 'https://connect.garmin.com/proxy/activity-service/activity/%s/details?maxChartSize=1000&maxPolylineSize=1000'

    def auth(self, force_login=None, force_password=None):
        '''
        Authentify session, using new CAS ticket
        See protocol on http://www.jasig.org/cas/protocol
        '''
        if force_login and force_password:
            # Login / Password from user form test
            login = force_login
            password = force_password
        else:
            # Decrypt password
            if not self.user.garmin_login and not force_login:
                raise Exception('Missing Garmin login')
            if not self.user.garmin_password and not force_password:
                raise Exception('Missing Garmin password')

            gpg = gnupg.GPG(gnupghome=self.GPG_HOME)
            login = self.user.garmin_login
            password = str(
                gpg.decrypt(
                    self.user.garmin_password,
                    passphrase=self.GPG_PASSPHRASE))
            if not password:
                raise Exception("No Garmin password available")

        user = GarminUser(login, password)
        if not user.authenticate():
            raise Exception('Garmin Authentication failure')
        self.session = user.session

        return user

    def list_tracks(self, page=0, nb_tracks=10):
        # Auth using stored login/pass
        if not self.session:
            self.auth()

        # Load paginated activities
        params = {
            'start': page * nb_tracks,
            'limit': nb_tracks,
        }
        resp = self.session.get(self.url_activity, params=params)
        data = resp.json()

        source = data['results'].get('activities', None)
        if source:
            source = [a['activity'] for a in source]

        return source

    def is_connected(self):
        return self.user.garmin_login is not None and self.user.garmin_password is not None

    def disconnect(self):
        # Just destroy credentials
        self.user.garmin_login = None
        self.user.garmin_password = None
        self.user.save()

    def get_activity_id(self, activity):
        return activity['activityId']

    def _load_extra_json(self, activity, data_type):
        # check in local cache
        try:
            check = None
            if data_type == 'laps':
                def check(x): return 'lapDTOs' in x
            f = self.get_file(
                activity,
                data_type,
                format_json=True,
                check=check)
            if f:
                return f
        except Exception as e:
            logger.warning('Invalid track file: {}'.format(e))

        # Load external json page
        activity_id = self.get_activity_id(activity)
        urls = {
            'laps': self.url_laps % activity_id,
            'polyline': self.url_polyline % activity_id,
        }
        if data_type not in urls:
            raise Exception("Invalid data type %s" % data_type)

        resp = self.session.get(urls[data_type])
        if resp.encoding is None:
            resp.encoding = 'utf-8'

        if resp.content == 'The requested endpoint is retired':
            raise Exception('Deprecated Garmin endpoint')

        # Store file locally
        self.store_file(activity, data_type, resp.content)

        return resp.json()

    def build_line_coords(self, activity):
        '''
        Extract coords from Garmin measurements
        '''

        # First, load details
        details = self._load_extra_json(activity, 'polyline')

        # Load metrics/measurements from file
        key = 'geoPolylineDTO'
        if key not in details:
            raise Exception("Unsupported format")
        base = details[key]
        if 'polyline' not in base:
            raise Exception("Missing polyline")

        # Build simplified polyline
        return [(float(x.get('lat', 0)), float(x.get('lon', 0)))
                for x in base['polyline']]

    def load_files(self, activity):
        # Load laps
        self._load_extra_json(activity, 'laps')

        # Load details
        self._load_extra_json(activity, 'polyline')

    def build_identity(self, activity):
        '''
        Extract Garmin data from raw activity
        '''
        identity = {}

        # Type of sport
        identity['sport'] = Sport.objects.get(
            slug=activity['activityType']['key'])
        logger.debug('Sport: %s' % identity['sport'])

        # Date
        t = int(activity['beginTimestamp']['millis']) / 1000
        identity['date'] = datetime.utcfromtimestamp(t).replace(tzinfo=utc)
        logger.debug('Date : %s' % identity['date'])

        # Time
        if False and 'sumMovingDuration' in activity:
            identity['time'] = timedelta(seconds=float(
                activity['sumMovingDuration']['value']))
        elif 'sumDuration' in activity:
            t = activity['sumDuration']['minutesSeconds'].split(':')
            identity['time'] = timedelta(
                minutes=float(
                    t[0]), seconds=float(
                    t[1]))
        else:
            raise Exception('No duration found.')
        logger.debug('Time : %s' % identity['time'])

        # Distance in km
        distance = activity.get('sumDistance')
        if distance:
            if distance['unitAbbr'] == 'm':
                identity['distance'] = float(distance['value']) / 1000.0
            else:
                identity['distance'] = float(distance['value'])
        else:
            identity['distance'] = 0.0
        logger.debug('Distance : %s km' % identity['distance'])

        # Speed
        identity['speed'] = time(0, 0, 0)
        if 'weightedMeanMovingSpeed' in activity:
            speed = activity['weightedMeanMovingSpeed']

            if speed['unitAbbr'] == 'km/h' or (
                    speed['uom'] == 'kph' and identity['sport'].get_category() != 'running'):
                # Transform km/h in min/km
                s = float(speed['value'])
                if s != 0.0:
                    mpk = 60.0 / s
                    hour = int(mpk / 60.0)
                    minutes = int(mpk % 60.0)
                    seconds = int((mpk - minutes) * 60.0)
                    identity['speed'] = time(hour, minutes, seconds)
            elif speed['unitAbbr'] == 'min/km':
                try:
                    identity['speed'] = datetime.strptime(
                        speed['display'], '%M:%S').time()
                except BaseException:
                    s = float(speed['value'])
                    if not math.isinf(s):
                        minutes = int(s)
                        identity['speed'] = time(
                            0, minutes, int((s - minutes) * 60.0))
        logger.debug('Speed : %s' % identity['speed'])

        # Elevation gain/loss
        identity['elevation_gain'] = 0.0
        if 'gainElevation' in activity:
            identity['elevation_gain'] = float(
                activity['gainElevation']['value'])
        identity['elevation_loss'] = 0.0
        if 'lossElevation' in activity:
            identity['elevation_loss'] = float(
                activity['lossElevation']['value'])
        logger.debug(
            'Elevation: +%f / -%f' %
            (identity['elevation_gain'],
             identity['elevation_loss']))

        # update name
        skip_titles = ('Sans titre', 'No title', )
        name = activity['activityName']['value']
        identity['name'] = name not in skip_titles and name or ''

        return identity

    def build_splits(self, activity):
        # Load laps
        laps = self._load_extra_json(activity, 'laps')
        laps = laps['lapDTOs']

        def _convert_date(lap, name):
            # Convert a timestamp to a datetime
            if name not in lap:
                return None
            return arrow.get(lap[name]).datetime

        def _convert_point(lap, name_lat, name_lng):
            # Build a point from lat,lng
            if name_lat not in lap or name_lng not in lap:
                return None
            return Point(float(lap[name_lat]), float(lap[name_lng]))

        # Build every split
        out = []
        for i, lap in enumerate(laps):
            split = TrackSplit(position=i + 1)
            split.elevation_min = lap.get('minElevation', 0.0)
            split.elevation_max = lap.get('maxElevation', 0.0)
            split.elevation_gain = lap.get('elevationGain', 0.0)
            split.elevation_loss = lap.get('elevationLoss', 0.0)
            split.speed_max = lap.get('maxSpeed', 0.0)
            split.speed = lap.get('averageSpeed', 0.0)
            split.distance = lap.get('distance', 0.0)
            split.time = lap.get('duration', 0.0)
            split.energy = lap.get('calories', 0.0)
            split.date_start = _convert_date(lap, 'startTimeGMT')
            split.date_end = split.date_start + timedelta(seconds=split.time)
            split.position_start = _convert_point(
                lap, 'startLatitude', 'startLongitude')
            split.position_end = None  # no data :/
            out.append(split)

        return out
