from django.core.cache import cache
from django.db.models import Count, Sum, Min
from django.utils.functional import cached_property
import sport
from calendar import monthrange
from datetime import timedelta, date
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


class SportStats(object):
    """
    Simple stats user/sport/session calculator
    """

    def __init__(self, user, year=None, use_all_sessions=False):
        '''
        Setup date boundaries for dataset
        By default, last 12 months
        '''
        self.user = user
        self.date = date.today()

        # List available years
        limits = sport.models.SportDay.objects.filter(week__user=self.user).aggregate(min=Min('date'))
        self.years = limits['min'] and \
            reversed(range(limits['min'].year, self.date.year + 1)) or \
            (self.date.year + 1,)

        year_delta = timedelta(days=365)
        if year is not None:
            # Full Year
            year = int(year)
            start = date(year=year, month=1, day=1)
            end = start + year_delta
            self.date_range = 'year'
            if year not in self.years or year <= 1900:  # strftime does not support below 1900
                raise Exception('Invalid year {}'.format(year))

        elif use_all_sessions is True:
            # All the months !
            end = self.date
            start = limits['min'] or date(year=self.date.year, month=1, day=1)
            self.date_range = 'all'

        else:
            # Default: last 12 months
            end = self.date
            start = end - year_delta
            self.date_range = 'last'

        # Load the StatsMonths
        d = start
        self.months = []
        sports = []
        while d < end:
            stat = StatsMonth(self.user, d.year, d.month)
            if stat.sports:
                sports += stat.sports.keys()
            self.months.append(stat)

            # Switch to next month
            _, nb_days = monthrange(d.year, d.month)
            d += timedelta(days=nb_days - d.day + 1)

        # Unique sports
        self.sports = sport.models.Sport.objects.filter(pk__in=set(sports))

    def get_sports(self):
        """
        List all the sport usage on the period
        """
        def _get_nb(month, sport):
            if not month.sports or sport.pk not in month.sports:
                return 0
            return month.sports[sport.pk]['nb'] or 0

        return [
            {
                'label': sport.name,
                'data' : [
                    _get_nb(month, sport)
                    for month in self.months
                ]
            }
            for sport in self.sports
        ]

    def get_distances(self):
        """
        List all distances on the period
        """
        return [
            month.distance or 0
            for month in self.months
        ]

    def get_hours(self):
        """
        List all total hours on the period
        """
        return [
            month.hours or 0
            for month in self.months
        ]

    def get_periods(self):
        """
        List all periods used to calculate these stats
        """
        return [
            {
                "name": "XXX",
                "timestamp": month.timestamp,
            }
            for month in self.months
        ]

#
#  // Build months urls
#  var urls = [{% for m in months %}'{{ url(url_month, *url_args + [m.year, m.month])}}',{% endfor %}];
#
