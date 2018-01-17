from django.core.cache import cache
from django.db.models import Count, Sum
from django.utils.functional import cached_property
import sport
from calendar import monthrange
from datetime import date
from helpers import week_to_date
import math


class StatsCached(object):
    '''
    Stats built & cached for quick access
    '''
    user = None
    prefix = None
    key = ''
    data = {}

    def __init__(self, user, prefix, preload=True):
        self.user = user

        # Build cache key
        key_parts = (
            self.user.pk,
            prefix,
            self.start.strftime('%d%m%Y'),
            self.end.strftime('%d%m%Y'),
        )
        self.key = 'stats:{}:{}:{}:{}'.format(*key_parts)

        # Initial fetch
        if preload:
            self.fetch()

    def __getattr__(self, name):
        if self.data and name in self.data:
            return self.data[name]

    def __str__(self):
        return u'%s : %s %s to %s' % (
            self.user.username, self.prefix, self.start, self.end)

    def fetch(self):
        self.data = cache.get(self.key)
        return self.data

    def save(self):
        # Save in cache, no expiry !
        cache.set(self.key, self.data, None)

    @cached_property
    def timestamp(self):
        # Used by flot js
        return int(self.start.strftime('%s'))

    def build(self):
        def _timedelta_to_hours(td):
            return td and math.ceil(td.total_seconds() / 3600) or 0

        # Fetch all sessions in the month
        filters = {
            'day__week__user': self.user,
            'day__date__gte': self.start,
            'day__date__lte': self.end,
        }
        sessions = sport.models.SportSession.objects.filter(**filters)
        sessions = sessions.exclude(plan_session__status='failed')

        # Get stats per types
        types = sessions.values('type').annotate(nb=Count('type'))
        types = dict((t['type'], t['nb']) for t in types)
        types.update({u'total': sessions.count()})

        # Get stats per sports
        sports = sessions.values('sport').annotate(
            nb=Count('sport'), distance=Sum('distance'), time=Sum('time'))
        sports = dict((s['sport'], {
            'distance': s['distance'],
            'time': s['time'],
            'hours': _timedelta_to_hours(s['time']),
            'nb': s['nb'],
        }) for s in sports)

        # Total stats
        total = sessions.aggregate(distance=Sum('distance'), time=Sum('time'))

        # Join data
        self.data = {
            'sessions': types,
            # total nb of days with sport
            'days': len(sessions.values('day').distinct()),
            'distance': total['distance'],
            'time': total['time'],
            'hours': _timedelta_to_hours(total['time']),
            'sports': sports,
        }

        # Save data
        self.save()

        return self.data


class StatsWeek(StatsCached):
    '''
    Represents a week of sport stats about a user
    '''
    year = None
    week = None

    def __init__(self, user, year, week, preload=True):
        self.year = year
        self.week = week

        super(StatsWeek, self).__init__(user, 'month', preload)

    @cached_property
    def start(self):
        # Start Date
        return week_to_date(self.year, self.week, 1)

    @cached_property
    def end(self):
        # End Date
        return week_to_date(self.year, self.week, 0)


class StatsMonth(StatsCached):
    '''
    Represents a month of sport stats about a user
    '''
    year = None
    month = None

    def __init__(self, user, year, month, preload=True):
        self.year = year
        self.month = month

        super(StatsMonth, self).__init__(user, 'month', preload)

    @cached_property
    def start(self):
        # Start Date
        return date(self.year, self.month, 1)

    @cached_property
    def end(self):
        # End Date
        _, last_day = monthrange(self.year, self.month)
        return date(self.year, self.month, last_day)
