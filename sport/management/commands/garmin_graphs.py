from django.core.management.base import BaseCommand, CommandError
from run.models import GarminActivity

class Command(BaseCommand):
  _min_date = None

  def handle(self, *args, **options):
    for id in args:
      try:
        self.graph(GarminActivity.objects.get(garmin_id=id))
      except GarminActivity.DoesNotExist:
        raise CommandError("Activity %s not found" % id)
      except Exception, e:
        raise e

  def graph(self, activity):
    print "Activity #%d %s of %s : %s" % (activity.id, activity.garmin_id, activity.user, activity.name)


    from pylab import *


    #X = np.linspace(-np.pi, np.pi, 256,endpoint=True)
    X = [1, 4, 10]
    Y = [10, 20, 30]

    plot(X,Y)


    show()
