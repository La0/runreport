from base import Track
from sport.models import Sport
from datetime import datetime, timedelta, time
import logging
from django.utils.timezone import utc

class GarminTrack(Track):
  class Meta:
    proxy = True

  def build_identity(self, data=None):
    '''
    Extract Garmin data from raw activity
    '''
    logger = logging.getLogger('coach.run.garmin')

    if data is None:
      data = self.get_data('raw')
    if data is None:
      raise Exception('Empty data for GarminActivity %s' % self)

    # Type of sport
    self.identity['sport'] = Sport.objects.get(slug=data['activityType']['key'])
    logger.debug('Sport: %s' % self.identity['sport'])

    # Date
    t = int(data['beginTimestamp']['millis']) / 1000
    self.identity['date'] = datetime.utcfromtimestamp(t).replace(tzinfo=utc)
    logger.debug('Date : %s' % self.identity['date'])

    # Time
    if False and 'sumMovingDuration' in data:
      self.identity['time'] = timedelta(seconds=float(data['sumMovingDuration']['value']))
    elif 'sumDuration' in data:
      t = data['sumDuration']['minutesSeconds'].split(':')
      self.identity['time'] = timedelta(minutes=float(t[0]), seconds=float(t[1]))
    else:
      raise Exception('No duration found.')
    logger.debug('Time : %s' % self.identity['time'])

    # Distance in km
    distance = data['sumDistance']
    if distance['unitAbbr'] == 'm':
      self.identity['distance'] =  float(distance['value']) / 1000.0
    else:
      self.identity['distance'] =  float(distance['value'])
    logger.debug('Distance : %s km' % self.identity['distance'])

    # Speed
    self.identity['speed'] = time(0,0,0)
    if 'weightedMeanMovingSpeed' in data:
      speed = data['weightedMeanMovingSpeed']

      if speed['unitAbbr'] == 'km/h' or (speed['uom'] == 'kph' and self.identity['sport'].get_category() != 'running'):
        # Transform km/h in min/km
        s = float(speed['value'])
        mpk = 60.0 / s
        hour = int(mpk / 60.0)
        minutes = int(mpk % 60.0)
        seconds = int((mpk - minutes) * 60.0)
        self.identity['speed'] = time(hour, minutes, seconds)
      elif speed['unitAbbr'] == 'min/km':
        try:
          self.identity['speed'] = datetime.strptime(speed['display'], '%M:%S').time()
        except:
          s = float(speed['value'])
          minutes = int(s)
          self.identity['speed'] = time(0, minutes, int((s - minutes) * 60.0))
    logger.debug('Speed : %s' % self.identity['speed'])

    # update name
    skip_titles = ('Sans titre', 'No title', )
    name = data['activityName']['value']
    self.identity['name'] = name not in skip_titles and name or ''

    return self.identity
