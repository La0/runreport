from strava import StravaProvider
from garmin import GarminProvider

def get_provider(name, user):
  # Helper to load a provider instance
  providers = {
    StravaProvider.NAME : StravaProvider,
    GarminProvider.NAME : GarminProvider,
  }
  if name not in providers:
    return None
  return providers[name](user)
