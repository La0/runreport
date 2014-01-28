from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from django.conf import settings

class Command(BaseCommand):

  def handle(self, *args, **options):
    if not settings.DEBUG:
      raise CommandError('This command should not be run in production !')
    self.reset(len(args) == 1 and args[0] or 'plop')

  def reset(self, password):
    for user in Athlete.objects.all():
      print user
      user.set_password(password)
      user.save()
    print 'Resetted those accounts with password %s' % password
