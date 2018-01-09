from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from club.models import ClubInvite
from optparse import make_option
from datetime import datetime
from django.db import IntegrityError
import json

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--sender',
      dest='sender',
      help='Username of the sender user'),
    make_option('--recipient-mail',
      dest='recipient-mail',
      help='Mail of the recipient'),
    make_option('--recipient-name',
      dest='recipient-name',
      help='Name of the recipient'),
    make_option('--json-list',
      dest='json',
      help='Path to a json file with multiple recipients.'),
  )

  sender = None

  def handle(self, *args, **options):
    # Load & check sender is super user
    try:
      self.sender = Athlete.objects.get(username=options['sender'])
      if not self.sender.is_superuser:
        raise Exception('Not a super user')
    except Exception as e:
      raise CommandError('Invalid sender : %s' % str(e))

    # Load unique recipient
    if options['recipient-mail']:
      self.build_invite(options['recipient-mail'], options['recipient-name'])

    # Load multiple recipients from json file
    if options['json']:
      with open(options['json'], 'r') as json_file:
        for r in json.load(json_file):
          self.build_invite(r['mail'], r['name'])

  def build_invite(self, recipient, name):

    # Build the invite
    data = {
      'sender' : self.sender,
      'type' : 'create',
      'recipient' : recipient,
      'name' : name,
    }
    try:
      invite = ClubInvite.objects.create(**data)
    except IntegrityError:
      print('Duplicate invitation for %s' % recipient)
      return
    print("Created invite %s for %s" % (invite.slug, recipient))

    # Send it !
    invite.send()
