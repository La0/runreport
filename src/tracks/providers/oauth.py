import requests
import urllib
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from random import randint
import base64
from hashlib import md5

class OauthProvider(object):
  auth_url = ''
  token_url = ''

  def build_user_state(self, seed=None):
    # Create a random hash token
    # so that access redirects are unique
    if not seed:
      seed = randint(1, 1000)
    h = md5('%d:%d:%s' % (seed, self.user.pk, settings.SECRET_KEY))
    return '%d.%s' % (seed, base64.b64encode(h.digest()))

  def build_redirect_url(self):
    # Build the redirect absolute url
    site = Site.objects.get(pk=settings.SITE_ID)

    return 'http://%s%s' % (site.domain, reverse('track-oauth', args=(self.NAME, )))

  def build_auth_url(self, args={}):
    '''
    Step 1 of the authentification
    Send user to provider login
    '''
    if not self.auth_url:
      raise Exception("Missing auth url")

    return  self.auth_url + '?' + urllib.urlencode(args)

  def exchange_token(self, args={}):
    '''
    Step 2 of the authentification
    Exchange the code from provider for an access token
    '''
    if not self.token_url:
      raise Exception("Missing token url")

    response = requests.post(self.token_url, data=args)
    if response.status_code != 200:
      print(response.text)
      raise Exception("Invalid response from %s" % self.token_url)

    return response

  def request(self, url, data=None, bearer=None, method='get'):
    # Support different methods
    methods = {
      'get' : requests.get,
      'post' : requests.post,
    }
    if method not in methods:
      raise Exception('Invalid request method %s' % method)

    # Helper to make simple authentified requests
    headers = {}
    if bearer:
      headers['Authorization'] = 'Bearer %s' % bearer

    return methods[method](url, data=data, headers=headers)
