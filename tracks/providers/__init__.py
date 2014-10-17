from strava import StravaProvider

def get_provider(name):
  # Helper to load a provider instance
  providers = {
    StravaProvider.NAME : StravaProvider
  }
  if name not in providers:
    return None
  return providers[name]()
