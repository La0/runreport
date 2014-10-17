from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from users.models import Athlete
from tracks.providers import get_provider

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--username',
      action='store',
      dest='username',
      type='string',
      default=False,
      help='Ran the import on the specified user.',
    ),
    make_option('--provider',
      action='store',
      dest='provider',
      type='string',
      default=False,
      help='Ran the import with this provider.',
    ),
  )
  user = None
  provider = None

  def handle(self, *args, **options):
    # Check input
    if not options['username']:
      raise CommandError("Missing usernam")
    if not options['provider']:
      raise CommandError("Missing provider")

    # Load user
    try:
      self.user = Athlete.objects.get(username=options['username'])
      print 'User #%d %s %s' % (self.user.id, self.user.first_name, self.user.last_name)
    except Exception, e:
      raise CommandError("Invalid user %s : %s" % (options['username'], str(e)))

    # Load provider
    self.provider = get_provider(options['provider'])
    if not self.provider:
      raise CommandError("Invalid provider %s" % options['provider'])

    # Display login url
    auth_url = self.provider.auth(self.user)
    print 'Login using : %s' % auth_url

    # Check tracks
    self.provider.check_tracks(self.user)

