from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from club.models import ClubInvite
from optparse import make_option
from datetime import datetime

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
    print 'Build invite for %s' % recipient


    # Build the invite
    data = {
      'sender' : self.sender,
      'type' : 'create',
      'recipient' : recipient,
    }
    invite = ClubInvite.objects.create(**data)
    print "Created invite : %s" % invite.slug

    # Send it !
    invite.send()
