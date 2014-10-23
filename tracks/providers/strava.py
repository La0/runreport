from base import TrackProvider
from oauth import OauthProvider
from helpers import gpolyline_decode, nameize
from datetime import datetime, timedelta
from sport.models import Sport
from tracks.models import TrackSplit

class StravaProvider(TrackProvider, OauthProvider):
  NAME = 'strava'
  settings = ['STRAVA_ID', 'STRAVA_SECRET', ]

  auth_url = 'https://www.strava.com/oauth/authorize'
  token_url = 'https://www.strava.com/oauth/token'
  activities_url = 'https://www.strava.com/api/v3/athlete/activities'
  activity_url = 'https://www.strava.com/api/v3/activities/%d'

  def auth(self):
    # Just build the auth url to redirect the user
    # on Strava
    args = {
      'client_id' : self.STRAVA_ID,
      'redirect_uri' : self.build_redirect_url(),
      'response_type' : 'code',
      'scope' : 'view_private', # Access to private sessions
      'state' : self.build_user_state(),
    }
    return self.build_auth_url(args)

  def get_token(self, code):

    # Ask for an access token
    args = {
      'client_id' : self.STRAVA_ID,
      'client_secret' : self.STRAVA_SECRET,
      'code' : code,
    }
    response = self.exchange_token(args)
    data = response.json()

    # Save the access token on user
    if 'access_token' not in data:
      raise Exception('No access token in response')
    self.user.strava_token = data['access_token']
    self.user.save()

    # Give athlete informations
    return data['athlete']

  def check_tracks(self, page=0, nb_tracks=10):
    if not self.user.strava_token:
      raise Exception('Missing Strava token for %s' % self.user.username)

    args = {
      'page' : page,
      'per_page' : nb_tracks,
    }
    response = self.request(self.activities_url, data=args, bearer=self.user.strava_token)
    if response.status_code != 200:
      raise Exception("No activities")

    activities = response.json()
    return self.import_activities(activities)

  def get_activity_id(self, activity):
    return activity['id']

  def load_files(self, activity):
    # No files to add
    pass

  def build_line_coords(self, activity):
    # First, load the details
    resp = self.request(self.activity_url % activity['id'], bearer=self.user.strava_token)
    if resp.status_code != 200:
      raise Exception("No activity %d" % (activity['id'], ))

    # Store details
    self.store_file(activity, 'details', resp.content)
    details = resp.json()

    # Decode the polyline
    return gpolyline_decode(details['map']['polyline'])

  def build_identity(self, activity):
    # Load details
    details = self.get_file(activity, 'details', format_json=True)

    # Load or create sport
    try:
      name = details['type']
      sport = Sport.objects.get(strava_name=name)
    except Sport.DoesNotExist, e:
      parent = Sport.objects.get(slug='all') # generic category
      sport = Sport.objects.create(name=name, slug=nameize(name), strava_name=name, parent=parent, depth=1)

    # Build identity
    return {
      'name' : details['name'],
      'distance' : details['distance'] / 1000.0,
      'date' : datetime.strptime(details['start_date'], '%Y-%m-%dT%H:%M:%SZ').date(),
      'time' : timedelta(seconds=details['elapsed_time']),
      'sport' : sport,
    }

  def build_splits(self, activity):
    return []
