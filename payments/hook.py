import poplib
import hashlib
import logging
import email
from django.conf import settings
from payments.models import PaymentEvent, PaymentSubscription
from users.models import Athlete
import json

logger = logging.getLogger('payments.hook')

class PaymillHook(object):
  pop = None # Connection to mail server

  def __init__(self):
    pass


  def run(self):
    '''
    Main Workflow
    '''
    logger.debug('Start Paymill hook check')

    # Connect & check
    self.connect()
    if not self.pop.getwelcome():
      logger.error('Connection to mail server failed')
      raise Exception('Connection to mail server failed')

    # Got any messages ?
    nb, _ = self.pop.stat()
    if not nb:
      logger.info('No messages to analyse')
      return

    # Loop on messages
    _, messages, __ = self.pop.list()
    for msg_id in messages:
      try:
        self.analyse(msg_id)
      except Exception, e:
        print 'Analysis failed for msg %s : %s' % (msg_id, str(e))

    # Commit transaction
    self.pop.quit()

  def connect(self):
    '''
    Connect to Mail server through POP3
    '''
    self.pop  = poplib.POP3_SSL(settings.PAYMILL_HOOK_SERVER)
    self.pop.user(settings.PAYMILL_HOOK_EMAIL)
    self.pop.pass_(settings.PAYMILL_HOOK_PASSWORD)

  def analyse(self, msg_id):
    '''
    Analyse a mail
    '''
    # Load it
    _, raw_msg, __ = self.pop.retr(msg_id)

    #print raw_msg
    msg = email.message_from_string('\r\n'.join(raw_msg))

    content = None
    if msg.is_multipart():
      # Search for raw text
      for part in msg.get_payload():
        if part.get_content_type() != 'text/html': # should match json
          content = part.get_payload(decode=True)
    else:
      content = msg.get_payload(decode=True)

    # Kill newline
    content = content.replace('\r\n', '')

    # Unique hash from raw content
    event_id = hashlib.md5(content).hexdigest()
    if PaymentEvent.objects.filter(event_id=event_id).count() > 0:
      raise Exception('Event already saved.')

    # Load & check hook
    hook_data = json.loads(content)
    event_data = hook_data.get('event')
    if not event_data:
      raise Exception('No event in json payload')
    event_type = event_data.get('event_type')
    if not event_type:
      raise Exception('No event type')
    event_category = event_type[:event_type.index('.')]
    event_resource = event_data.get('event_resource')
    if not event_resource:
      raise Exception('No event resource')

    # Save event in db
    data = {
      'event_id' : event_id,
      'type' : event_type,
      'raw_data' : event_resource,
    }
    if event_category == 'client':
      try:
        data['user'] = Athlete.objects.get(paymill_id=event_resource['id'])
      except Athlete.DoesNotExist:
        pass
    if event_category == 'subscription':
      try:
        data['user'] = PaymentSubscription.objects.get(paymill_id=event_resource['id'])
      except PaymentSubscription.DoesNotExist:
        pass
    event = PaymentEvent.objects.create(**data)

    # Delete message from server
    self.pop.dele(msg_id)

    return event
