import requests
import gnupg
from coach.settings import GPG_HOME, GPG_KEY, GPG_PASSPHRASE

class GarminConnector:
  _user = None
  _login = None
  _password = None

  _url_login = 'https://connect.garmin.com/signin'
  _url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'

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

  def search(self):
    params = {
      'start' : 0,
      'limit' : 10,
    }
    resp = self._session.get(self._url_activity, params=params)
    data = resp.json()

    from pprint import pprint

    for activity in data['results']['activities']:
      activity = activity['activity']
      #pprint(activity)

      print "#%s %s : %s %s au kilo sur %s km" % (activity['activityId'], activity['activityName']['value'], activity['sumMovingDuration']['display'], activity['weightedMeanMovingSpeed']['display'], activity['sumDistance']['value'])
