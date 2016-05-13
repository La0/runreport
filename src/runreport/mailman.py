from django.conf import settings
from mailmanclient import Client
import logging

logger = logging.getLogger('mailman')

class MailMan(object):
  '''
  Use official mailman 3.0 api client
  '''
  client = None
  connected = False
  lists = []

  def __init__(self):

    # Create settings & check connection
    try:
      self.client = Client(settings.MAILMAN_URL, settings.MAILMAN_USER, settings.MAILMAN_PASS)
      logger.debug('Connected to mailman %(mailman_version)s' % self.client.system)
    except:
      logger.error('Connection to mailman failed on %s' % settings.MAILMAN_URL)
      return None

    self.connected = True


  def get_list(self, list_name):
    '''
    Retrieve a list using only its name
    '''
    if not self.connected:
      raise Exception('No mailman connection')

    list_name += '@%s' % settings.MAILMAN_DOMAIN
    ml = self.client.get_list(list_name)
    if not ml:
      raise Exception('Mailing list %s not found' % list_name)

    return ml

  def subscribe(self, list_name, email, full_name):
    '''
    Subscribe a member to a mailing list
    With full approval directly
    '''
    if not self.connected:
      raise Exception('No mailman connection')

    ml = self.get_list(list_name)
    return ml.subscribe(email, full_name, pre_verified=True, pre_confirmed=True, pre_approved=True)

  def unsubscribe(self, list_name, email):
    '''
    Unsubscribe a member from a mailing list
    '''
    if not self.connected:
      raise Exception('No mailman connection')

    ml = self.get_list(list_name)
    return ml.unsubscribe(email)

  def create_list(self, list_name, full_name, extra_settings=None):
    '''
    Create a new mailing list properly configured
    '''

    # Retrieve domain
    domain = self.client.get_domain(settings.MAILMAN_DOMAIN)
    if not domain:
      raise Exception('No mailman domain %s' % settings.MAILMAN_DOMAIN)

    # Get or create list on domain
    try:
        ml = domain.create_list(list_name)
    except:
        ml = self.get_list(list_name)

    # Configure mailing
    mls = ml.settings
    mls['default_member_action'] = 'accept'
    mls['default_nonmember_action'] = 'accept'
    mls['send_welcome_message'] = False
    mls['advertised'] = False
    mls['display_name'] = full_name
    mls['subject_prefix'] = '[%s] ' % full_name
    mls['reply_to_address'] = ml.fqdn_listname

    # Override
    if extra_settings:
      # No update on mls
      for k,v in extra_settings.items():
        mls[k] = v

    mls.save()

    return ml

  def delete_list(self, list_name):
    '''
    Delete a mailing list
    '''
    if not self.connected:
      raise Exception('No mailman connection')

    ml = self.get_list(list_name)
    return ml.delete()

  def list_subscriptions(self, email):
    """
    List all subscriptions for a user
    """
    if not self.connected:
      raise Exception('No mailman connection')

    user = self.client.get_user(email)
    return user.subscriptions
