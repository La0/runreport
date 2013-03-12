import requests
import gnupg
from datetime import datetime
from coach.settings import GPG_HOME, GPG_PASSPHRASE
from run.models import GarminActivity, RunSession
import json
from django.utils.timezone import utc

class GarminConnector:
  _user = None
  _login = None
  _password = None

  _url_login = 'https://connect.garmin.com/signin'
  _url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'

  _max_activities = 10 # per request

  def __init__(self, user=None, login=None, password=None):
    if user:
      # Load from user
      self._user = user
      profile = self._user.get_profile()
      if profile is None:
        raise Exception("No profile for user %s" % self._user)
      self._login = profile.garmin_login
      self.load_password(profile.garmin_password)

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
    r = self._session.get(self._url_login)

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
      except KeyError, e:
        pass # Invalid activity
      except Exception, e:
        raise e

    return activities

  def load_activity(self, activity):
    # Load existing activity
    #  or build a new one
    created = False
    try:
      act = GarminActivity.objects.get(garmin_id=activity['activityId'], user=self._user)
    except:
      act = GarminActivity(garmin_id=activity['activityId'], user=self._user)
      created = True
  
    # Init newly created activity
    if created:

      # Date
      t = int(activity['beginTimestamp']['millis']) / 1000
      act.date = datetime.utcfromtimestamp(t).replace(tzinfo=utc)

      # Time
      t = float(activity['sumMovingDuration']['value'])# - 3600 # Add one hour otherwise :/ Timezone ?
      act.time = datetime.utcfromtimestamp(t).time()

      # Distance
      act.distance =  float(activity['sumDistance']['value'])

      # Speed
      act.speed = datetime.strptime(activity['weightedMeanMovingSpeed']['display'], '%M:%S').time()

    # Always update name & raw json
    act.name = activity['activityName']['value']
    act.raw_json = json.dumps(activity)

    act.save()

    # Try to map a run session
    try:
      sess = RunSession.objects.get(date=act.date.date(), report__user=self._user, garmin_activity=None)
      sess.garmin_activity = act
      sess.save()
    except:
      pass

    return act
