from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from plan.models import Plan
from optparse import make_option
from datetime import date
import random
from sport.models import Sport
from helpers import date_to_day

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--username',
      dest='username',
      help='Username of the plan creator'),
    make_option('--sessions',
      dest='sessions',
      default=5,
      help='Nb of sessions to build'),
  )


  def handle(self, *args, **kwargs):
    try:
      self.user = Athlete.objects.get(username=kwargs['username'])
    except Athlete.DoesNotExist:
      raise CommandError('No user %s' % kwargs['username'])

    # Init plan
    start = date_to_day(date.today())
    self.plan = Plan.objects.create(name='Generated Plan %s' % self.user.first_name, creator=self.user, start=start)

    sport = Sport.objects.get(slug='running')

    # Add sessions
    nb = int(kwargs['sessions'])
    for i in range(0, nb):
      print 'Add session %d' % i

      data = {
        'week' : random.randint(0, nb / 2),
        'day' : random.randint(0, 6),
        'name' : 'session %d' % i,
        'sport' : sport,
      }
      print data
      self.plan.sessions.create(**data)

    # Publish plan
    self.plan.publish(Athlete.objects.filter(username=kwargs['username']))
