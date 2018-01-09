from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from badges.models import BadgeCategory
from optparse import make_option

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--user',
      dest='user',
      help='Username of one user to match'),
    make_option('--dry-run',
      dest='dry-run',
      action='store_true',
      default=False,
      help='Do not apply any changes'),
  )

  def handle(self, *args, **options):

    # Filter users
    users = Athlete.objects.filter(is_active=True)
    if options['user']:
      users = users.filter(username=options['user'])
    if not users:
      raise CommandError('No users found.')

    for user in users:
      print('User %s' % user)
      user.find_badges(not options['dry-run'])

