from django.core.management.base import BaseCommand, CommandError
from run.garmin import GarminConnector
from run.models import GarminActivity
from users.models import Athlete
from coach.settings import REPORT_START_DATE
from datetime import datetime
from django.utils.timezone import utc
import logging
from optparse import make_option

logger = logging.getLogger('coach.run.garmin')

class Command(BaseCommand):
  _min_date = None
  option_list = BaseCommand.option_list + (
    make_option('--username',
      action='store',
      dest='username',
      type='string',
      default=False,
      help='Ran the import on the specified user.'),
    make_option('--offline',
      action='store_true',
      dest='offline',
      default=False,
      help='Use only data from local json files'),
    )

  def handle(self, *args, **options):

    # Load min date
    min_year, min_week = REPORT_START_DATE
    self._min_date = datetime.strptime('%d %d 1' % (min_year, min_week), '%Y %W %w').replace(tzinfo=utc)

    # Just one user ?
    if options['username']:
      logger.info('Loading user : %s' % options['username'])
      user = Athlete.objects.get(username=options['username'])
      if options['offline']:
        self.update_user_offline(user)
      else:
        self.import_user(user)

    # Browse all users
    else:
      users = Athlete.objects.filter(garmin_login__isnull=False, garmin_password__isnull=False)
      users = users.exclude(garmin_login='') # don't use empty logins
      for user in users:
        if options['offline']:
          self.update_user_offline(user)
        else:
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
      logger.error("Login failed for %s: %s" % (user, str(e)))
      return

    # Import activities !
    nb = 0
    while True:
      activities = []
      try:
        activities = gc.search(nb)
        nb += 1
      except Exception, e:
        logger.error("Import failed for %s: %s" % (user, str(e)))

      # End of loop ?
      if not len(activities):
        break
      min_date = min([a.date for a in activities])
      if min_date <= self._min_date:
        break

  def update_user_offline(self, user):
    '''
    Update a user, only for existing activities
    '''
    activities = GarminActivity.objects.filter(user=user)
    for act in activities:
      logger.info("%s : Offline activity %s" % (user.username, act.garmin_id))
      try:
        act.update()
        act.save()
      except Exception, e:
        logger.error("Update failed: %s" % (str(e),))
