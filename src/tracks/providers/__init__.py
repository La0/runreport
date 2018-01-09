from .strava import StravaProvider
from .garmin import GarminProvider

PROVIDERS = {
    GarminProvider.NAME: GarminProvider,
    StravaProvider.NAME: StravaProvider,
}


def get_provider(name, user):
    # Helper to load a provider instance
    if name not in PROVIDERS:
        return None
    return PROVIDERS[name](user)


def all_providers(user):
    return [p(user) for p in PROVIDERS.values()]
