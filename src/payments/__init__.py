
def get_api():
    '''
    Helper to load MangoPay API
    '''
    from mangopaysdk.mangopayapi import MangoPayApi
    import requests
    from django.conf import settings
    import os
    api = MangoPayApi()

    # Auth
    api.Config.ClientID = settings.MANGOPAY_ID
    api.Config.ClientPassword = settings.MANGOPAY_SECRET

    # Cache
    api.Config.TempPath = settings.MANGOPAY_CACHE
    if not os.path.exists(settings.MANGOPAY_CACHE):
        os.makedirs(settings.MANGOPAY_CACHE)

    # Endpoint
    if settings.MANGOPAY_PROD:
        api.Config.BaseUrl = "https://api.mangopay.com"
    else:
        api.Config.BaseUrl = "https://api.sandbox.mangopay.com"

    # SSL, use requests cacert
    requests_dir = os.path.dirname(os.path.abspath(requests.__file__))
    api.Config.SSLVerification = os.path.join(requests_dir, 'cacert.pem')
    if not os.path.exists(api.Config.SSLVerification):
        raise Exception(
            'Missing SSL CA cert in %s' %
            api.Config.SSLVerification)

    return api


def get_notification_hash(event_type):
    '''
    Helper to auth a notification
    from MangoPay
    '''
    from django.conf import settings
    import hashlib
    contents = 'mangopay:%s:%s' % (event_type, settings.SECRET_KEY, )
    return hashlib.md5(contents).hexdigest()
