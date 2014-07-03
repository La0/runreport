from django.core.cache import cache
from django.db.models import Count, Sum
from models import SportSession
from calendar import monthrange
from datetime import date
import math

class StatsMonth:
  '''
  Represents a month of sport stats about a user
  '''
  user = None
  year = None
  month = None
  key = ''
  data = {}

  def __init__(self, user, year, month):
    self.user = user
    self.year = year
    self.month = month
    
    # Build cache key
    self.key = 'stats:%s:%s:%s' % (self.user.username, self.year, self.month)

    # Initial fetch
    self.fetch()

  def __getattr__(self, name):
    if self.data and name in self.data:
      return self.data[name]

  def date(self):
    # Gives time of month
    return date(year=self.year, month=self.month, day=1)

  def timestamp(self):
    return int(self.date().strftime('%s'))

  def fetch(self):
    self.data = cache.get(self.key)
    return self.data

  def timedelta_to_hours(self, td):
    if not td:
      return 0
    return math.ceil(td.total_seconds() / 3600)

  def build(self):

    # Start and end dates
    _, last_day = monthrange(self.year, self.month)
    start = date(self.year, self.month, 1)
    end = date(self.year, self.month, last_day)

    # Fetch all sessions in the month
    sessions = SportSession.objects.filter(day__week__user=self.user, day__date__gte=start, day__date__lte=end)

    # Get stats per types
    types = sessions.values('type').annotate(nb=Count('type'))
    types = dict((t['type'], t['nb']) for t in types)
    types.update({u'total' : sessions.count()})

    # Get stats per sports
    sports = sessions.values('sport').annotate(nb=Count('sport'), distance=Sum('distance'), time=Sum('time'))
    sports = dict((s['sport'], {
      'distance' : s['distance'],
      'time' : s['time'],
      'hours' : self.timedelta_to_hours(s['time']),
    }) for s in sports)

    # Total stats
    total = sessions.aggregate(distance=Sum('distance'), time=Sum('time'))

    # Join data
    self.data = {
      'sessions' : types,
      'days' : len(sessions.values('day').distinct()), # total nb of days with sport
      'distance' : total['distance'],
      'time' : total['time'],
      'hours' : self.timedelta_to_hours(total['time']),
      'sports' : sports,
    }

    # Save in cache, no expiry !
    cache.set(self.key, self.data, None)

    return self.data
