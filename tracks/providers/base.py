from django.conf import settings
import logging
import json
from django.db import transaction
from django.db.models import Min, Max, Count
import hashlib
from tracks.models import Track, TrackSplit, TrackFile
from sport.stats import StatsMonth, StatsWeek
from helpers import date_to_week

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
  def is_connected(self):
    '''
    True if the current user is connected to the provider
    '''
    raise NotImplementedError('Please implement this method')

  def disconnect(self):
    '''
    Disconnect current user from this provider
    '''
    raise NotImplementedError('Please implement this method')


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

  def build_splits(self, activity):
    '''
    Build stats for an activity
    '''
    raise NotImplementedError('Please implement this method')

  def store_file(self, activity, name, data):
    # Store locally a file awaiating save on a track
    activity_id = self.get_activity_id(activity)
    if activity_id not in self.files:
      self.files[activity_id] = {}
    self.files[activity_id][name] = data

  def get_file(self, activity, name, format_json=False):
    # Get localy stored file in memory
    activity_id = self.get_activity_id(activity)
    if activity_id in self.files and name in self.files[activity_id]:
      out = self.files[activity_id][name]
      return format_json and json.loads(out) or out

    # Get file from disk
    try:
      tf = TrackFile.objects.get(track__provider_id=activity_id, name=name)
      return tf.get_data(format_json)
    except TrackFile.DoesNotExist:
      pass
    return None

  def imported_stats(self):
    '''
    Gives simple stats about imported tracks
    '''
    tracks = Track.objects.filter(provider=self.NAME, session__day__week__user=self.user)
    stats = tracks.aggregate(min_date=Min('session__day__date'), max_date=Max('session__day__date'), total=Count('id'))
    return stats

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
    weeks = []
    while True:
      tracks = []
      try:
        tracks = self.check_tracks(nb)

        # Get the months & weeks to refresh stats
        for t in tracks:
          date = t.session.day.date
          m = (date.year, date.month)
          w = date_to_week(date)
          if m not in months:
            months.append(m)
          if w not in weeks:
            weeks.append(m)
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

    # Refresh months stats cache
    for year,month in months:
      logger.info("Refresh month stats %d/%d for %s" % (month, year, self.user))
      st = StatsMonth(self.user, year, month, preload=False)
      st.build()

    # Refresh weeks stats cache
    for year,week in weeks:
      logger.info("Refresh week stats %d/%d for %s" % (week, year, self.user))
      st = StatsWeek(self.user, week, month, preload=False)
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
      act = None
      try:
        with transaction.atomic():
          act, updated = self.build_track(activity)
          if act:
            activities.append(act)
            if updated:
              updated_nb += 1
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
    activity_id = self.get_activity_id(activity)
    activity_raw = json.dumps(activity)
    try:
      track = Track.objects.get(provider=self.NAME, provider_id=activity_id)

      # Check the activity needs an update
      # by comparing md5
      track_file = track.get_file('raw')
      if track_file and track_file.md5 == hashlib.md5(activity_raw).hexdigest():
        logger.info("Existing %s activity %s did not change" % (self.NAME, activity_id))
        return track, False

      logger.info("Existing %s activity %s needs update" % (self.NAME, activity_id))
    except Track.DoesNotExist, e:
      track = Track(provider=self.NAME, provider_id=activity_id)
      logger.info("Created %s activity %s" % (self.NAME, activity_id))
    except Exception, e:
      logger.error("Failed to import %s activity %s : %s" % (self.NAME, activity_id, str(e)))
      return None, None

    # Build optional simplified polyline
    if not track.simple:
      try:
        coords = self.build_line_coords(activity)
        track.simplify(coords)
      except Exception, e:
        logger.warn('No polyline: %s' % (str(e), ))

    identity = self.build_identity(activity)
    if not hasattr(track, 'session'):
      # Attach to a session
      track.attach_session(self.user, identity)

    elif identity['name'] and not track.session.name:
      # Update title
      track.session.name = identity['name']
      track.session.save()


    # Save full track
    track.save()
    logger.info("Saved %s track #%d"% (self.NAME, track.pk))

    # Store raw activity
    self.store_file(activity, 'raw', activity_raw)

    # Save files when we are sure to have a PK
    self.load_files(activity)
    for name, data in self.files[activity_id].items():
      track.add_file(name, data)
      logger.info("%s track #%d added file %s"% (self.NAME, track.pk, name))

    # Finally, attach splits
    self.attach_splits(track, activity)

    # Build image (needs pk)
    try:
      track.build_image()
      track.build_thumb()
      track.save()
    except Exception, e:
      logger.warn('No image: %s' % (str(e), ))

    return track, True

  def attach_splits(self, track, activity):
    '''
    Build & attach the splits outside
    of main track build
    '''
    splits = self.build_splits(activity)
    self.build_total(track, splits)


  def build_total(self, track, splits):
    '''
    Build a total TrackSplit from a list of splits
    '''
    total = TrackSplit(position=0)
    total.track_id = track.pk
    total.distance = 0
    total.time = 0

    # List all current splits per positions
    positions = dict([(s['position'], s['pk']) for s in track.splits.values('pk', 'position')])
    positions_updated = []

    for s in splits:

      # Update totals
      total.distance += s.distance
      total.time += s.time
      s.distance_total = total.distance
      s.time_total = total.time

      # Update existing split ?
      if s.position in positions:
        s.id = positions[s.position]
      positions_updated.append(s.position)

      s.track_id = track.pk
      s.save()
      logger.debug("%s track #%d added split %d"% (self.NAME, s.track_id, s.position))

    # Save main split
    nb = len(splits)
    total.distance_total = total.distance
    total.time_total = total.time
    if nb > 0:
      total.speed = sum([s.speed for s in splits]) / nb
      total.speed_max = min([s.speed_max for s in splits])
      total.elevation_min = min([s.elevation_min for s in splits])
      total.elevation_max = max([s.elevation_max for s in splits])
      total.elevation_gain = sum([s.elevation_gain for s in splits])
      total.elevation_loss = sum([s.elevation_loss for s in splits])
      total.energy = sum([s.energy for s in splits])

    if nb >= 2:
      start = splits[0]
      total.date_start = start.date_start
      total.position_start = start.position_start

      end = splits[nb - 1]
      total.date_end = end.date_end
      total.position_end = end.position_end

    # Update total split ?
    total_pk = positions.get(0)
    if total_pk:
      total.pk = total_pk
    positions_updated.append(0)

    total.save()
    track.split_total = total
    track.save()

    # Cleanup useless splits
    diff = set(positions.keys()).difference(positions_updated)
    if positions and diff:
        logger.debug('Cleanup splits on positions %s' % diff)
        track.splits.filter(position__in=diff).delete()

    return total
