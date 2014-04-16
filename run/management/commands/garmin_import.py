from django.core.management.base import BaseCommand, CommandError
from run.models import GarminActivity
from users.models import Athlete
from run.garmin import GarminConnector
from datetime import datetime
from django.utils.timezone import utc
import logging
from optparse import make_option

logger = logging.getLogger('coach.run.garmin')

class Command(BaseCommand):
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

    # Just one user ?
    if options['username']:
      logger.info('Loading user : %s' % options['username'])
      user = Athlete.objects.get(username=options['username'])
      if options['offline']:
        self.update_user_offline(user)
      else:
        GarminConnector.import_user(user)

    # Browse all users
    elif options['offline']:
      users = Athlete.objects.filter(garmin_login__isnull=False, garmin_password__isnull=False)
      users = users.exclude(garmin_login='') # don't use empty logins
      for user in users:
        if options['offline']:
          self.update_user_offline(user)
        else:
          GarminConnector.import_user(user)

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
