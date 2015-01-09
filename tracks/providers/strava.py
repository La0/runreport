from base import TrackProvider
from oauth import OauthProvider
from helpers import gpolyline_decode, nameize
from datetime import datetime, timedelta
from sport.models import Sport
from tracks.models import TrackSplit
from dateutil.parser import parse

class StravaProvider(TrackProvider, OauthProvider):
  NAME = 'strava'
  settings = ['STRAVA_ID', 'STRAVA_SECRET', ]

  auth_url = 'https://www.strava.com/oauth/authorize'
  deauth_url = 'https://www.strava.com/oauth/deauthorize'
  token_url = 'https://www.strava.com/oauth/token'
  activities_url = 'https://www.strava.com/api/v3/athlete/activities'
  activity_url = 'https://www.strava.com/api/v3/activities/%d'

  def is_connected(self):
    return self.user.strava_token is not None

  def disconnect(self):
    # Request to destroy token
    self.request(self.deauth_url, bearer=self.user.strava_token, method='post')

    # Just destroy credentials
    self.user.strava_token = None
    self.user.save()

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
      'page' : page + 1, # pages start at 1
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
      'date' : parse(details['start_date']).date(),
      'time' : timedelta(seconds=details['elapsed_time']),
      'sport' : sport,
    }

  def build_splits(self, activity):
    # Load details
    details = self.get_file(activity, 'details', format_json=True)
    if 'splits_metric' not in details:
      return []

    # Import every metric split
    out = []
    for s in details['splits_metric']:
      split = TrackSplit(position=s['split'])
      split.time = s['elapsed_time']
      split.distance = s['distance']
      if split.time > 0:
        split.speed = split.distance / split.time
      if s['elevation_difference'] > 0:
        split.elevation_gain = s['elevation_difference']
      else:
        split.elevation_loss = abs(s['elevation_difference'])

      out.append(split)

    return out
