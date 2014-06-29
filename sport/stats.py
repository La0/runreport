from django.core.cache import cache
from django.db.models import Count, Sum
from models import SportSession
from calendar import monthrange
from datetime import date

class StatsMonth:
  '''
  Represents a month of sport stats about a user
  '''
  user = None
  year = None
  month = None
  key = ''

  def __init__(self, user, year, month):
    self.user = user
    self.year = year
    self.month = month
    
    # Build cache key
    self.key = 'stats:%s:%s:%s' % (self.user.username, self.year, self.month)

  def fetch(self):
    return cache.get(self.key)

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
    sports = dict((s['sport'], {'distance' : s['distance'], 'time' : s['time']}) for s in sports)

    # Total stats
    total = sessions.aggregate(distance=Sum('distance'), time=Sum('time'))

    # Join data
    data = {
      'sessions' : types,
      'days' : len(sessions.values('day').distinct()), # total nb of days with sport
      'distance' : total['distance'],
      'time' : total['time'],
      'sports' : sports,
    }

    # Save in cache
    cache.set(self.key, data)

    return data
