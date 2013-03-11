from django.core.management.base import BaseCommand, CommandError
from run.garmin import GarminConnector
from django.contrib.auth.models import User
from coach.settings import REPORT_START_DATE
from datetime import datetime

class Command(BaseCommand):
  _min_date = None

  def handle(self, *args, **options):
    # Load min date
    min_year, min_week = REPORT_START_DATE
    self._min_date = datetime.strptime('%d %d 1' % (min_year, min_week), '%Y %W %w')

    # Browse users
    users = User.objects.exclude(userprofile__garmin_login=None)
    for user in users:
      self.import_user(user)

  def import_user(self, user):
    '''
    Import all offers until min time
    '''
    # Try to login
    gc = None
    try:
      gc = GarminConnector(user)
      gc.login()
    except Exception, e:
      print "Error on login for %s: %s" % (user, str(e))

    # Import activities !
    nb = 0
    while True:
      activities = []
      try:
        activities = gc.search(nb)
        nb += 1
      except Exception, e:
        print "Error on import for %s: %s" % (user, str(e))

      # End of loop ?
      if not len(activities):
        break
      min_date = min([a.date for a in activities])
      if min_date <= self._min_date:
        break

