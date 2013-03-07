import requests

class GarminConnector:

  _url_login = 'https://connect.garmin.com/signin'
  _url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'

  def __init__(self, login, password):
    self._login = login
    self._password = password

  def login(self):
    '''
    Authentify session
    '''
    print 'Login with %s' % self._login

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
      'limit' : 5,
    }
    resp = self._session.get(self._url_activity, params=params)
    data = resp.json()
    from pprint import pprint
    pprint(data)

