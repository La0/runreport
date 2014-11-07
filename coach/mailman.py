from django.conf import settings
import requests

class MailMan(object):
  '''
  Use mailman-api to talk to a mailman server
  http://mailman-api.readthedocs.org/en/stable/api.html
  '''
  lists = []

  def __init__(self):
    try:
      self.get_lists()
    except Exception, e:
      print 'Failed to load mailman lists: %s' % (str(e), )

  def get_lists(self):
    '''
    Retrieve all mailing lists
    '''
    if not settings.MAILMAN_URL:
      raise Exception('No mailman url defined')

    resp = requests.get(settings.MAILMAN_URL)
    if resp.status_code != 200:
      raise Exception('Invalid mailman response %d : %s' % (resp.status_code, resp.content))

    self.lists = resp.json()
    return self.lists

  def get_members(self, list_name):
    '''
    List all members in a mailing list
    '''
    if list_name not in self.lists:
      return False

    resp = requests.get(settings.MAILMAN_URL + '/' + list_name)
    if resp.status_code != 200:
      raise Exception('Invalid mailman response %d : %s' % (resp.status_code, resp.content))

    return resp.json()

  def subscribe(self, list_name, email, full_name, digest=False):
    '''
    Subscribe a member to a mailing list
    '''
    if list_name not in self.lists:
      return False

    data = {
      'address' : email,
      'fullname' : full_name,
      'digest' : digest,
    }
    resp = requests.put(settings.MAILMAN_URL + '/' + list_name, data=data)
    if resp.status_code == 409:
      # Already a member
      return False
    if resp.status_code != 200:
      raise Exception('Invalid mailman response %d : %s' % (resp.status_code, resp.content))

    return resp.json()

  def unsubscribe(self, list_name, email):
    '''
    Unsubscribe a member from a mailing list
    '''
    if list_name not in self.lists:
      return False

    data = {
      'address' : email,
    }
    resp = requests.delete(settings.MAILMAN_URL + '/' + list_name, data=data)
    if resp.status_code == 404:
      # Not a member
      return False
    if resp.status_code != 200:
      raise Exception('Invalid mailman response %d : %s' % (resp.status_code, resp.content))

    return resp.json()

