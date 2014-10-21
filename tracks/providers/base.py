from django.conf import settings
import logging

logger = logging.getLogger('coach.sport.garmin')

class TrackSkipUpdateException(Exception):
  '''
  Used when an update for an user is not realy needed
  '''
  pass

class TrackEndImportException(Exception):
  '''
  Used when there are no more tracks to import
  '''
  pass


class TrackProvider:
  NAME = '' # used in urls slugs
  settings = [] # Names of settings needed
  user = None # User owning the tracks

  def __init__(self, user):
    self.user = user

    # Check and copy app settings
    for s in self.settings:
      if not hasattr(settings, s):
        raise Exception("Missing setting %s" % s)
      setattr(self, s, getattr(settings, s))

  def import_user(self, full=False):
    '''
    Do the import for an user
    '''
    # Try to login
    try:
      self.auth()
    except Exception, e:
      logger.error("Login failed for %s: %s" % (self.user, str(e)))
      return

    # Import tracks !
    nb = 0
    months = [] # to build stats cache
    while True:
      tracks = []
      try:
        tracks = self.check_tracks(nb)

        # Get the months to refresh stats
        for t in tracks:
          if 'date' not in t.identity:
            logger.error("No date on track identity #%d : no stats refresh." % t.pk)
          date = t.identity['date']
          m = (date.year, date.month)
          if m not in months:
            months.append(m)
        nb += 1
      except TrackSkipUpdateException, e:
        if full:
          nb += 1
          continue
        logger.info("Update not needed for %s" % (self.user,))
        break
      except TrackEndImportException, e:
        logger.info("No more tracks to import for %s" % (self.user,))
      except Exception, e:
        logger.error("Import failed for %s: %s" % (self.user, str(e)))
        break

      # End of loop ?
      if not len(tracks):
        break

    # Refresh stats cache
    for year,month in months:
      logger.info("Refresh stats %d/%d for %s" % (month, year, self.user))
      st = StatsMonth(self.user, year, month, preload=False)
      st.build()

