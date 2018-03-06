from rest_framework.generics import RetrieveAPIView, ListAPIView
from api.mixins import UserAPIMixin, DayMixin, WeekMixin, MonthMixin, YearMixin
from django.shortcuts import get_object_or_404
from sport.models import Sport, SportDay, SportWeek
from sport.serializers import StatsSerializer, SportSerializer, SportDaySerializer, SportWeekSerializer
from sport.stats import SportStats



class SportList(ListAPIView):
    """
    List all available sports
    """
    serializer_class = SportSerializer
    queryset = Sport.objects.filter(depth__gte=1).order_by('depth', 'name')


class CalendarDay(UserAPIMixin, DayMixin, RetrieveAPIView):
    """
    Loads a specific day & attached sessions
    """
    serializer_class = SportDaySerializer

    def get_object(self):
        return get_object_or_404(
            SportDay,
            week__user=self.get_user(),
            date=self.start.date(),
        )

class CalendarWeek(UserAPIMixin, WeekMixin, RetrieveAPIView):
    """
    Loads a specific week & attached days + sessions
    """
    serializer_class = SportWeekSerializer

    def get_object(self):
        return get_object_or_404(
            SportWeek,
            user=self.get_user(),
            year=self.year,
            week=self.week,
        )

class CalendarMonth(UserAPIMixin, MonthMixin, ListAPIView):
    """
    Loads all days+sessions in a month
    """
    # TODO: should use a lighter serializer
    serializer_class = SportDaySerializer

    def get_queryset(self):
        return SportDay.objects.filter(
            week__user=self.get_user(),
            date__gte=self.start,
            date__lte=self.end,
        ).order_by('date')


class CalendarYear(UserAPIMixin, YearMixin, ListAPIView):
    """
    Loads all day+sessions in a year
    """
    # TODO: should use a lighter serializer
    serializer_class = SportDaySerializer

    def get_queryset(self):
        return SportDay.objects.filter(
            week__user=self.get_user(),
            date__gte=self.start,
            date__lte=self.end,
        ).order_by('date')


class StatsView(UserAPIMixin, RetrieveAPIView):
    """
    Build stats for a user
    """
    serializer_class = StatsSerializer

    def get_object(self):
        """
        Calc stats on user instance
        and store results on local serializer instance
        """
        return SportStats(
            user=self.get_user(),
            year=self.kwargs.get('year'),
            use_all_sessions=self.kwargs.get('all'),
        )
