# coding=utf-8
import requests
import gnupg
from datetime import datetime, time
from coach.settings import GPG_HOME, GPG_PASSPHRASE
from sport.models import GarminActivity
import logging
import re
from helpers import week_to_date
from django.db import transaction
import hashlib
import json
from sport.stats import StatsMonth

logger = logging.getLogger('coach.sport.garmin')

class GarminAuthException(Exception):
  pass

class GarminSkipUpdateException(Exception):
  '''
  Used when an update for an user is not realy needed
  '''
  pass

class GarminEndException(Exception):
  '''
  Used when there are no more activities to import
  '''
  pass

class GarminConnector:
  _user = None
  _login = None
  _password = None

  # Login Urls
  _url_hostname = 'http://connect.garmin.com/gauth/hostname'
  _url_login = 'https://sso.garmin.com/sso/login'
  _url_post_login = 'http://connect.garmin.com/post-auth/login'
  _url_check_login = 'http://connect.garmin.com/user/username'

  # Data Urls
  _url_activity = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities'
  _url_laps = 'http://connect.garmin.com/proxy/activity-service-1.3/json/activity/%s'
  _url_details = 'http://connect.garmin.com/proxy/activity-service-1.3/json/activityDetails/%s'

  _max_activities = 20 # per request

  def __init__(self, user=None, login=None, password=None):
    if user:
      # Load from user
      self._user = user
      self._login = self._user.garmin_login
      self.load_password(self._user.garmin_password)

    elif login and password:
      # Load from login/pass
      self._login = login
      self._password = password
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
    Authentify session, using new CAS ticket
    See protocol on http://www.jasig.org/cas/protocol
    '''
    if not self._password:
      raise Exception("No Garmin password available")

    self._session = requests.Session()

    # Get SSO server hostname
    res = self._session.get(self._url_hostname)
    sso_hostname = res.json().get('host', None)
    if not sso_hostname:
      raise GarminAuthException('No SSO server available')

    # Load login page to get login ticket
    params = {
      'clientId' : 'GarminConnect',
      'webhost' : sso_hostname,
    }
    res = self._session.get(self._url_login, params=params)
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
      'username' : self._login,
      'password' : self._password,
    }
    res = self._session.post(self._url_login, params=params, data=data)
    if res.status_code != 200:
      raise GarminAuthException('Authentification failed.')

    # Second auth step
    # Don't know why this one is necessary :/
    res = self._session.get(self._url_post_login)
    if res.status_code != 200:
      raise GarminAuthException('Second auth step failed.')

    # Check login
    res = self._session.get(self._url_check_login)
    user = res.json()
    if not user.get('username', None):
      raise GarminAuthException("Login check failed.")
    logger.info('Logged in as %s' % (user['username']))

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
    updated_nb = 0
    if 'activities' not in data['results']:
      raise GarminEndException()

    for activity in data['results']['activities']:
      try:
        activity = activity['activity']
        with transaction.atomic():
          act, updated = self.load_activity(activity)
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
      raise GarminSkipUpdateException()

    return activities

  def load_activity(self, activity):
    # Load existing activity
    #  or build a new one
    created = False
    activity_id = activity['activityId']
    try:
      act = GarminActivity.objects.get(garmin_id=activity_id , user=self._user)

      # Check the activity needs an update
      # by comparing md5
      if act.md5_raw == hashlib.md5(json.dumps(activity)).hexdigest():
        logger.info("%s : Existing activity %s did not change" % (self._user.username, activity_id))
        return act, False

      logger.info("%s : Existing activity %s needs update" % (self._user.username, activity_id))
    except GarminActivity.DoesNotExist, e:
      act = GarminActivity(garmin_id=activity_id, user=self._user)
      created = True
      logger.info("%s : Created activity %s" % (self._user.username, activity_id))
    except Exception, e:
      logger.error("%s : Failed to import activity %s : %s" % (self._user.username, activity_id, str(e)))
      return None, None

    # Update raw data
    act.update(activity)

    # Always update json file
    act.set_data('raw', activity)

    # Load supplementary infos
    if created:
      self.load_json(act, 'laps')
      self.load_json(act, 'details')

    act.save()

    return act, True

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
    if resp.encoding is None:
      resp.encoding = 'utf-8'
    activity.set_data(data_type, resp.json())
    return True

  @staticmethod
  def import_user(user, full=False):
    '''
    Do the import for an users
    '''
    # Try to login
    gc = None
    try:
      gc = GarminConnector(user)
      gc.login()
    except Exception, e:
      logger.error("Login failed for %s: %s" % (user, str(e)))
      return

    # Import activities !
    nb = 0
    months = [] # to build stats cache
    while True:
      activities = []
      try:
        activities = gc.search(nb)
        for a in activities:
          m = (a.date.year, a.date.month)
          if m not in months:
            months.append(m)
          print m
        print months
        nb += 1
      except GarminSkipUpdateException, e:
        if full:
          nb += 1
          continue
        logger.info("Update not needed for %s" % (user,))
        break
      except GarminEndException, e:
        logger.info("No more activities to import for %s" % (user,))
      except Exception, e:
        logger.error("Import failed for %s: %s" % (user, str(e)))
        break

      # End of loop ?
      if not len(activities):
        break

    # Refresh stats cache
    for year,month in months:
      logger.info("Refresh stats %d/%d for %s" % (month, year, user))
      st = StatsMonth(user, year, month, preload=False)
      st.build()
