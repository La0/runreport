from base import TrackProvider, TrackSkipUpdateException, TrackEndImportException
import requests
import gnupg
import re
import logging
from django.db import transaction
from tracks.models import GarminTrack
from django.contrib.gis.geos import LineString
import json
import hashlib

logger = logging.getLogger('coach.sport.garmin')

class GarminAuthException(Exception):
  '''
  Used when the specific garmin login process fails
  '''
  pass

class GarminProvider(TrackProvider):
  NAME = 'garmin'
  settings = ['GPG_HOME', 'GPG_PASSPHRASE', ]

  # Login Urls
  url_hostname = 'http://connect.garmin.com/gauth/hostname'
  url_login = 'https://sso.garmin.com/sso/login'
  url_post_login = 'http://connect.garmin.com/post-auth/login'
  url_check_login = 'http://connect.garmin.com/user/username'

  # Data Urls
  url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'
  url_laps = 'http://connect.garmin.com/proxy/activity-service-1.3/json/activity/%s'
  url_details = 'http://connect.garmin.com/proxy/activity-service-1.3/json/activityDetails/%s'

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
      password = str(gpg.decrypt(self.user.garmin_password, passphrase=self.GPG_PASSPHRASE))
      if not password:
        raise Exception("No Garmin password available")

    self.session = requests.Session()

    # Get SSO server hostname
    res = self.session.get(self.url_hostname)
    sso_hostname = res.json().get('host', None)
    if not sso_hostname:
      raise GarminAuthException('No SSO server available')

    # Load login page to get login ticket
    params = {
      'clientId' : 'GarminConnect',
      'webhost' : sso_hostname,
    }
    res = self.session.get(self.url_login, params=params)
    if res.status_code != 200:
      raise GarminAuthException('No login form')

    # Get the login ticket value
    regex = '<input\s+type="hidden"\s+name="lt"\s+value="(?P<lt>\w+)"\s+/>'
    res = re.search(regex, res.text)
    if not res:
      raise GarminAuthException('No login ticket')
    login_ticket = res.group('lt')

    # Login/Password with login ticket
    # Send through POST
    data = {
      '_eventId' : 'submit', # Strange, but needed
      'lt' : login_ticket,
      'username' : login,
      'password' : password,
    }
    res = self.session.post(self.url_login, params=params, data=data)
    if res.status_code != 200:
      raise GarminAuthException('Authentification failed.')

    # Second auth step
    # Don't know why this one is necessary :/
    res = self.session.get(self.url_post_login)
    if res.status_code != 200:
      raise GarminAuthException('Second auth step failed.')

    # Check login
    res = self.session.get(self.url_check_login)
    garmin_user = res.json()
    if not garmin_user.get('username', None):
      raise GarminAuthException("Login check failed.")
    logger.info('Logged in as %s' % (garmin_user['username']))

    return garmin_user

  def check_tracks(self, page=0, nb_tracks=10):
    # Auth using stored login/pass
    if not self.session:
      self.auth()

    # Load paginated activities
    params = {
      'start' : page * nb_tracks,
      'limit' : nb_tracks,
    }
    resp = self.session.get(self.url_activity, params=params)
    data = resp.json()

    activities = []
    updated_nb = 0
    if 'activities' not in data['results']:
      raise TrackEndImportException()
    for activity in data['results']['activities']:
      try:
        activity = activity['activity']
        with transaction.atomic():
          act, updated = self.build_track(activity)
          if act:
            activities.append(act)
            if updated:
              updated_nb += 1
          else:
            transaction.rollback()
      except Exception, e:
        logger.error('Activity import failed: %s' % (str(e),))

    # When no update has been made, stop import
    if updated_nb == 0:
      raise TrackSkipUpdateException()

    return activities

  def build_track(self, activity):
    # Load existing activity
    #  or build a new one
    created = False
    activity_id = activity['activityId']
    activity_raw = json.dumps(activity)
    try:
      track = GarminTrack.objects.get(provider=self.NAME, provider_id=activity_id)

      # Check the activity needs an update
      # by comparing md5
      track_file = track.get_file('raw')
      if track_file.md5 == hashlib.md5(activity_raw).hexdigest():
        logger.info("Existing activity %s did not change" % (activity_id))
        return track, False

      logger.info("Existing activity %s needs update" % (activity_id))
    except GarminTrack.DoesNotExist, e:
      track = GarminTrack(provider=self.NAME, provider_id=activity_id)
      created = True
      logger.info("Created activity %s" % (activity_id))
    except Exception, e:
      logger.error("Failed to import activity %s : %s" % (activity_id, str(e)))
      return None, None

    # Load map from details
    if not track.raw:
      details = self.load_extra_json(track, 'details')
      track.raw = self.build_line(json.loads(details))
      track.simplify() # Build simplified line too

    # Update session
    track.build_identity(activity)
    track.attach_session(self.user)

    # Save full track
    track.save()

    # Save files when we are sure to have a PK
    track.add_file('raw', activity_raw)
    if created:
      track.add_file('details', details)
      track.add_file('laps', self.load_extra_json(track, 'laps'))

    return track, True


  def load_extra_json(self, track, data_type):
    # Load external json page
    urls = {
      'laps'    : self.url_laps % track.provider_id,
      'details' : self.url_details % track.provider_id,
    }
    if data_type not in urls:
      raise Exception("Invalid data type %s" % data_type)

    resp = self.session.get(urls[data_type])
    if resp.encoding is None:
      resp.encoding = 'utf-8'
    return resp.content # raw data



  def build_line(self, details):
    '''
    Build a geo track from Garmin measurements
    '''
    # Check session
    if not self.session:
      raise Exception("A SportSession is needed to build a track")
    if hasattr(self.session, 'track'):
      raise Exception("The SportSession has already a track")

    # Load metrics/measurements from file
    key = 'com.garmin.activity.details.json.ActivityDetails'
    if key not in details:
      raise Exception("Unsupported format")
    base = details[key]
    if 'measurements' not in base:
      raise Exception("Missing measurements")
    if 'metrics' not in base:
      raise Exception("Missing metrics")

    # Search latitude / longitude positions in measurements
    measurements = dict([(m['key'], m['metricsIndex']) for m in base['measurements']])
    if 'directLatitude' not in measurements or 'directLongitude' not in measurements:
      raise Exception("Missing lat/lon measurements")

    # Build linestring from metrics
    coords = []
    for m in base['metrics']:
      if 'metrics' not in m:
        continue
      lat, lng = m['metrics'][measurements['directLatitude']], m['metrics'][measurements['directLongitude']]
      if lat == 0.0 and lng == 0.0:
        continue
      coords.append((lat, lng))

    return LineString(coords)
