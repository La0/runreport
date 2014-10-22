from django.conf import settings
import logging
import json
from django.contrib.gis.geos import LineString
from django.db import transaction
import hashlib
from tracks.models import Track

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
  files = {} # local cache of download files

  def __init__(self, user):
    self.user = user

    # Check and copy app settings
    for s in self.settings:
      if not hasattr(settings, s):
        raise Exception("Missing setting %s" % s)
      setattr(self, s, getattr(settings, s))

  # Abtract methods to implement
  def get_activity_id(self, activity):
    '''
    Just give the id from an activity
    '''
    raise NotImplementedError('Please implement this method')

  def load_files(self, activity):
    '''
    Load additional files to attach to the track
    '''
    raise NotImplementedError('Please implement this method')

  def build_line_coords(self, activity):
    '''
    Build a list of the future map coords
    '''
    raise NotImplementedError('Please implement this method')

  def build_identity(self, activity):
    '''
    Build identity of an activity to macth session
    '''
    raise NotImplementedError('Please implement this method')

  def store_file(self, activity, name, data):
    # Store locally a file awaiating save on a track
    activity_id = self.get_activity_id(activity)
    if activity_id not in self.files:
      self.files[activity_id] = {}
    self.files[activity_id][name] = data

  def get_file(self, activity, name, format_json=False):
    # Get loccaly stored file
    activity_id = self.get_activity_id(activity)
    if activity_id in self.files and name in self.files[activity_id]:
      out = self.files[activity_id][name]
      return format_json and json.loads(out) or out
    return None

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
          date = t.session.day.date
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
        if settings.DEBUG:
          raise e
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

  def import_activities(self, source=None):
    '''
    Generic method iterating through activities list
    and calling build_track on everey one
    '''
    if not source:
      raise TrackEndImportException()

    activities = []
    updated_nb = 0
    for activity in source:
      try:
        with transaction.atomic():
          act, updated = self.build_track(activity)
          if act:
            activities.append(act)
            if updated:
              updated_nb += 1
          else:
            transaction.rollback()
      except Exception, e:
        if settings.DEBUG:
          raise e
        logger.error('%s activity import failed: %s' % (self.NAME, str(e),))

    # When not enough source activities, it's the end
    if len(source) < 10:
      raise TrackEndImportException()

    # When no update has been made, stop import
    if updated_nb == 0:
      raise TrackSkipUpdateException()

    return activities

  def build_track(self, activity):
    '''
    Generic track builder flow, from any activity
    Will call methods from the proxy subclass of Track
    '''
    # Load existing activity
    #  or build a new one
    created = False
    activity_id = self.get_activity_id(activity)
    activity_raw = json.dumps(activity)
    try:
      track = Track.objects.get(provider=self.NAME, provider_id=activity_id)

      # Check the activity needs an update
      # by comparing md5
      track_file = track.get_file('raw')
      if track_file.md5 == hashlib.md5(activity_raw).hexdigest():
        logger.info("Existing %s activity %s did not change" % (self.NAME, activity_id))
        return track, False

      logger.info("Existing %s activity %s needs update" % (self.NAME, activity_id))
    except Track.DoesNotExist, e:
      track = Track(provider=self.NAME, provider_id=activity_id)
      created = True
      logger.info("Created %s activity %s" % (self.NAME, activity_id))
    except Exception, e:
      logger.error("Failed to import %s activity %s : %s" % (self.NAME, activity_id, str(e)))
      return None, None

    # Store raw activity
    self.store_file(activity, 'raw', activity_raw)

    # Build map
    if not track.raw:
      coords = self.build_line_coords(activity)
      track.raw = LineString(coords)
      track.simplify() # Build simplified line too

    # Update session
    identity = self.build_identity(activity)
    track.attach_session(self.user, identity)

    # Save full track
    track.save()
    logger.info("Saved %s track #%d"% (self.NAME, track.pk))

    # Save files when we are sure to have a PK
    self.load_files(activity)
    for name, data in self.files[activity_id].items():
      track.add_file(name, data)
      logger.info("%s track #%d added file %s"% (self.NAME, track.pk, name))

    return track, True
