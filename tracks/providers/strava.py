from oauth import OauthProvider

class StravaProvider(OauthProvider):
  NAME = 'strava'
  settings = ['STRAVA_ID', 'STRAVA_SECRET', ]

  auth_url = 'https://www.strava.com/oauth/authorize'
  token_url = 'https://www.strava.com/oauth/token'
  activities_url = 'https://www.strava.com/api/v3/athlete/activities'

  def auth(self, user):
    # Just build the auth url to redirect the user
    # on Strava
    args = {
      'client_id' : self.STRAVA_ID,
      'redirect_uri' : self.build_redirect_url(),
      'response_type' : 'code',
      'scope' : 'view_private', # Access to private sessions
      'state' : self.build_user_state(user),
    }
    return self.build_auth_url(args)

  def get_token(self, user, code):

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
    user.strava_token = data['access_token']
    user.save()

    # Give athlete informations
    return data['athlete']

  def check_tracks(self, user, nb=10, page=1):
    if not user.strava_token:
      raise Exception('Missing Strava token for %s' % user.username)

    args = {
      'page' : page,
      'per_page' : nb,
    }
    response = self.request(self.activities_url, data=args, bearer=user.strava_token)
    if response.status_code != 200:
      raise Exception("No activities")

    print response.json()
