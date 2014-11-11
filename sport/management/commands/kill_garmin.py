from django.core.management.base import BaseCommand, CommandError
from sport.models import GarminActivity

class Command(BaseCommand):

  def handle(self, *args, **options):
    acts = GarminActivity.objects.all()
    acts = acts.exclude(session__track__isnull=False)
    acts = acts.filter(user__username='romain_bohdanowicz') # TRASHME
    acts = acts.filter(garmin_id='476998669')
    nb = acts.count()
    for i, act in enumerate(acts):
      try:
        print '%d/%d : %s %s' % (i, nb, act.user, act.garmin_id)
        act.to_track()
      except Exception, e:
        print 'Failed : %s' % str(e)
