from django.conf import settings
from django.contrib.sites.models import Site
from requests_oauthlib import OAuth2Session
from django.core.urlresolvers import reverse
from sport.models import SportSession

GAUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GTOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GREFRESH_URL = GTOKEN_URL
GCAL_SCOPE = [
  'https://www.googleapis.com/auth/calendar'
]

class GCalSync(object):
  '''
  Synchronize a user runreport Calendar
  with its Google Calendar Account
  '''
  user = None
  token = None
  google = None

  def __init__(self, user):
    self.user = user

    def __save_token(token):
      self.token = token

    # Dirty fix for updated scope issue
    # See https://github.com/requests/requests-oauthlib/issues/157
    import os
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "1"

    # Init google session
    url = reverse('gcal-oauth')
    scheme = settings.DEBUG and 'http' or 'https'
    site = Site.objects.get(pk=settings.SITE_ID)
    redirect_uri = '%s://%s%s' % (scheme, site.domain, url)
    args = {
      'redirect_uri' : redirect_uri,
      'scope' : GCAL_SCOPE,
      'auto_refresh_kwargs' : {
        'client_id' : settings.GCAL_CLIENT_ID,
        'client_secret' : settings.GCAL_CLIENT_SECRET,
      },
      'auto_refresh_url' : GREFRESH_URL,
      'token_updater' : __save_token,
    }
    self.google = OAuth2Session(settings.GCAL_CLIENT_ID, **args)

    # Init access token from refresh
    if self.user.gcal_token:
        self.google.refresh_token(GREFRESH_URL, refresh_token=self.user.gcal_token)

  def get_auth_url(self):
    '''
    First auth step, to redirect user on a Google url
    '''
    if self.user.gcal_token:
      raise Exception('User already has a google token')

    # access_type and approval_prompt are Google specific extra
    # parameters.
    authorization_url, state = self.google.authorization_url(GAUTH_URL, access_type="offline", approval_prompt="force")

    return authorization_url

  def exchange_token(self, code):
    '''
    Second auth step, to exchange code for token
    '''
    if self.user.gcal_token:
      raise Exception('User already has a google token')


    # Exhange token
    token = self.google.fetch_token(GTOKEN_URL, client_secret=settings.GCAL_CLIENT_SECRET, code=code)

    # Save refresh token
    self.token = token['access_token']
    self.user.gcal_token = token['refresh_token']
    self.user.save()

    return token


  def list_calendars(self):
    '''
    List all the calendars for current user
    '''
    resp = self.google.get('https://www.googleapis.com/calendar/v3/users/me/calendarList')
    if resp.status_code != 200:
        return None

    return resp.json()

  def get_calendar(self, calendar_id):
    '''
    Get details about a calendar
    '''
    url = 'https://www.googleapis.com/calendar/v3/calendars/%s' % calendar_id
    resp = self.google.get(url)

    if resp.status_code != 200:
        return None

    return resp.json()

  def create_calendar(self, summary):
    '''
    Create a new calendar
    '''
    if self.user.gcal_id:
      raise Exception('Already a calendar for this user')

    url = 'https://www.googleapis.com/calendar/v3/calendars'
    data = {
      'summary' : summary,
    }
    resp = self.google.post(url, json=data)

    if resp.status_code != 200:
        return None

    # Save calendar id
    data = resp.json()
    self.user.gcal_id = data['id']
    self.user.save()

    return data

  def sync_sport_session(self, session):
    '''
    sync a sport session in calendar
    '''
    if not self.user.gcal_id:
      raise Exception('No calendar available for this user')

    url = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % (self.user.gcal_id, )

    # Serialize session as Gcal
    description = '\n'.join([
      '%s %s' % (session.type, session.sport),
      session.comment or '',
    ])
    dt = session.day.date.strftime('%Y-%m-%d')
    data = {
      'summary' : session.name or '-',
      'description' : description,
      'start' : {
        'date' : dt,
      },
      'end' : {
        'date' : dt,
      },
      'source' : {
        'title' : 'RunReport',
        'url' : session.day.absolute_url,
      },
    }

    if session.gcal_id:
      # Update the event
      url += '/%s' % session.gcal_id
      resp = self.google.patch(url, json=data)

    else:
      # Create the event
      resp = self.google.post(url, json=data)

    if resp.status_code != 200:
      raise Exception('Failed to create event')

    # Save gcal id
    event = resp.json()
    if not session.gcal_id:
      session.gcal_id = event['id']
      session.save_base(raw=True) # No signals / loop

    return event

  def delete_event(self, event_id):
    '''
    Delete an event from user calendar
    '''
    url = 'https://www.googleapis.com/calendar/v3/calendars/%s/events/%s' % (self.user.gcal_id, event_id)
    resp = self.google.delete(url)

    if resp.status_code != 200:
      raise Exception('Failed to delete event')

    return resp.json()

  def cleanup(self):
    '''
    Cleanup all calendar sync traces
    '''

    # Remove token & id
    self.user.gcal_token = None
    self.user.gcal_id = None
    self.user.save()

    # Remove all id from Sport sessions
    sessions = SportSession.objects.filter(day__week__user=self.user, gcal_id__isnull=False)
    sessions.update(gcal_id=None)
