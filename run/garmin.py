import requests
import gnupg
from datetime import datetime, time
from coach.settings import GPG_HOME, GPG_PASSPHRASE
from run.models import GarminActivity, RunSession, RunReport
from django.utils.timezone import utc
from helpers import date_to_week
import logging

logger = logging.getLogger('coach.run.garmin')

class GarminConnector:
  _user = None
  _login = None
  _password = None

  _url_login = 'https://connect.garmin.com/signin'
  _url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'
  _url_laps = 'http://connect.garmin.com/proxy/activity-service-1.3/json/activity/%s'
  _url_details = 'http://connect.garmin.com/proxy/activity-service-1.3/json/activityDetails/%s'

  _max_activities = 10 # per request

  def __init__(self, user=None, login=None, password=None):
    if user:
      # Load from user
      self._user = user
      self._login = self._user.garmin_login
      self.load_password(self._user.garmin_password)

    elif login and password:
      # Load from login/pass
      self._login = login
      self.load_password(password)
    else:
      raise Exception("Missing login infos")

  def load_password(self, password):
    '''
    Try to decrypt password
    '''
    gpg = gnupg.GPG(gnupghome=GPG_HOME)
    self._password = str(gpg.decrypt(password, passphrase=GPG_PASSPHRASE))

  def login(self):
    '''
    Authentify session
    '''
    # First request is empty to init session
    self._session = requests.Session()
    self._session.get(self._url_login)

    # Setup form data
    data = {
      'login' : 'login',
      'login:loginUsernameField' : self._login,
      'login:password' : self._password,
      'login:rememberMe' : 'on',
      'login:signInButton' : 'Se connecter',
      'javax.faces.ViewState' : 'j_id1',
    }

    # Mimic firefox headers
    headers = {
      'Content-Type' : 'application/x-www-form-urlencoded',
      'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
      'Referer' : 'https://connect.garmin.com/signin',
      'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language' : 'en-us,en;q=0.5',
      'Accept-Encoding' : 'gzip, deflate',
    }

    # Send everything together through POST
    self._session.post(self._url_login, data=data, headers=headers)

    # Check we have auth cookie
    if 'org.jboss.seam.security.authtoken' not in self._session.cookies:
      raise Exception("Auth failed with login %s" % self._login)

  def search(self, nb_pass=0):
    if self._user is None:
      raise Exception("Can not search without a user")
    params = {
      'start' : nb_pass * self._max_activities,
      'limit' : self._max_activities,
    }
    resp = self._session.get(self._url_activity, params=params)
    data = resp.json()

    activities = []
    for activity in data['results']['activities']:
      try:
        activity = activity['activity']
        activities.append(self.load_activity(activity))
      except Exception, e:
        logger.error('Activity import failed: %s' % (str(e),))

    return activities

  def load_activity(self, activity):
    # Load existing activity
    #  or build a new one
    created = False
    activity_id = activity['activityId']
    try:
      act = GarminActivity.objects.get(garmin_id=activity_id , user=self._user)
      logger.info("%s : Existing activity %s" % (self._user.username, activity_id))
    except:
      act = GarminActivity(garmin_id=activity_id, user=self._user)
      created = True
      logger.info("%s : Created activity %s" % (self._user.username, activity_id))

    # Init newly created activity
    if created:

      # Date
      t = int(activity['beginTimestamp']['millis']) / 1000
      act.date = datetime.utcfromtimestamp(t).replace(tzinfo=utc)
      logger.debug('Date : %s' % act.date)

      # Time
      if 'sumMovingDuration' in activity:
        t = float(activity['sumMovingDuration']['value'])
        act.time = datetime.utcfromtimestamp(t).time()
      elif 'sumDuration' in activity:
        t = activity['sumDuration']['display']
        act.time = datetime.strptime(t, '%H:%M:%S').time()
      else:
        raise Exception('No duration found.')
      logger.debug('Time : %s' % act.time)

      # Distance
      act.distance =  float(activity['sumDistance']['value'])
      logger.debug('Distance : %s' % act.distance)

      # Speed
      if 'weightedMeanMovingSpeed' in activity:
        try:
          act.speed = datetime.strptime(activity['weightedMeanMovingSpeed']['display'], '%M:%S').time()
        except:
          print activity['weightedMeanMovingSpeed']
          act.speed = time(0,0,0)
      else:
        act.speed = time(0,0,0)
      logger.debug('Speed : %s' % act.speed)

    # Always update name & raw json
    act.name = activity['activityName']['value']
    act.set_data('raw', activity)

    # Load supplementary infos
    self.load_json(act, 'laps')
    self.load_json(act, 'details')

    act.save()

    # Try to map a run session
    try:
      date = act.date.date()
      week, year = date_to_week(date)
      report,_ = RunReport.objects.get_or_create(user=self._user, year=year, week=week)
      sess,_ = RunSession.objects.get_or_create(date=date, report=report)
      modified = False
      if sess.garmin_activity is None:
        sess.garmin_activity = act
        modified = True

      fields = {
        'name' : act.name != 'Sans titre' and act.name or None,
        'time' : act.time,
        'distance': act.distance,
        'comment' : activity['activityDescription']['value'] or None,
      }
      for f,v in fields.items():
        if v and not getattr(sess, f):
          setattr(sess, f, v)
          modified = True
      if modified:
        sess.save()
    except Exception, e:
      logger.error('%s : Failed to map %s to a RunSession. %s' % (self._user.username, activity_id, str(e) ))

    return act

  def load_json(self, activity, data_type):
    '''
    Load external json page, store it raw in model
    '''
    urls = {
      'laps'    : self._url_laps % activity.garmin_id,
      'details' : self._url_details % activity.garmin_id,
    }
    if data_type not in urls:
      raise Exception("Invalid data type %s" % data_type)

    if getattr(activity, 'md5_%s' % data_type) is not None:
      return False

    resp = self._session.get(urls[data_type])
    activity.set_data(data_type, resp.json())
    return True
