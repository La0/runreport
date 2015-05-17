import poplib
import logging
import email
from django.conf import settings

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
      # TODO: try catch here
      self.analyse(msg_id)

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

    print raw_msg
    msg = email.message_from_string('\r\n'.join(raw_msg))

    content = None
    if msg.is_multipart():
      # Search for raw text
      for part in msg.get_payload():
        print part.get_content_type()
    else:
      content = msg.get_payload()

    print content

    # TODO: delete message from server
    # self.pop.dele(msg_id)
