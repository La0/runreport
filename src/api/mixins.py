from users.models import Athlete
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from datetime import date, datetime
from helpers import week_to_date
import calendar


class UserAPIMixin(object):
    """
    Load user from url kwargs
    """
    def get_user(self):

        user = get_object_or_404(Athlete, username=self.kwargs['username'])

        # TODO: check rights

        return user


    def get_object(self):
        # Default object is asked user
        return self.get_user()


class DateMixin(object):
    def check_int_range(self, name, min_value, max_value):
        assert isinstance(name, str)
        assert isinstance(min_value, int)
        assert isinstance(max_value, int)
        try:
            value = int(self.kwargs[name])
            assert min_value <= value <= max_value
        except:
            raise Http404('Invalid {}'.format(name))

        return value


class YearMixin(DateMixin):
    """
    Loads a year from url
    """
    @cached_property
    def year(self):
        return self.check_int_range('year', 1900, 2100)

    @cached_property
    def start(self):
        return date(self.year, 1, 1)

    @cached_property
    def end(self):
        return date(self.year, 12, 31)


class MonthMixin(YearMixin):
    """
    Loads a month from url
    """
    @cached_property
    def month(self):
        return self.check_int_range('month', 1, 12)

    @cached_property
    def start(self):
        # Supports leap year
        start, _ = calendar.monthrange(self.year, self.month)
        return date(self.year, self.month, start)

    @cached_property
    def end(self):
        _, end = calendar.monthrange(self.year, self.month)
        return date(self.year, self.month, end)


class DayMixin(MonthMixin):
    """
    Loads a day from url
    """
    @cached_property
    def day(self):
        return self.check_int_range('day', 1, 31)

    @cached_property
    def start(self):
        return datetime(self.year, self.month, self.day, 0, 0)

    @cached_property
    def end(self):
        return datetime(self.year, self.month, self.day, 23, 59)


class WeekMixin(YearMixin):
    """
    Loads a week from url
    """
    @cached_property
    def week(self):
        return self.check_int_range('week', 1, 53)

    @cached_property
    def start(self):
        return week_to_date(self.year, self.week, day=1)

    @cached_property
    def end(self):
        return week_to_date(self.year, self.week, day=0)
