from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from club.models import ClubInvite
from optparse import make_option
from datetime import datetime
from django.db import IntegrityError

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--sender',
      dest='sender',
      help='Username of the sender user'),
    make_option('--recipient',
      dest='recipient',
      help='Mail of the recipient'),
  )

  sender = None

  def handle(self, *args, **options):
    # Load & check sender is super user
    try:
      self.sender = Athlete.objects.get(username=options['sender'])
      if not self.sender.is_superuser:
        raise Exception('Not a super user')
    except Exception, e:
      raise CommandError('Invalid sender : %s' % str(e))

    if options['recipient']:
      self.build_invite(options['recipient'])

  def build_invite(self, recipient):

    # Build the invite
    data = {
      'sender' : self.sender,
      'type' : 'create',
      'recipient' : recipient,
    }
    try:
      invite = ClubInvite.objects.create(**data)
    except IntegrityError:
      print 'Duplicate invitation for %s' % recipient
      return
    print "Created invite %s for %s" % (invite.slug, recipient)

    # Send it !
    invite.send()
