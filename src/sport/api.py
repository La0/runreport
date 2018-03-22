from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from api.mixins import UserAPIMixin, DayMixin, WeekMixin, MonthMixin, YearMixin
from django.shortcuts import get_object_or_404
from sport.models import Sport, SportDay, SportWeek, SportSession
from sport.serializers import StatsSerializer, SportSerializer, SportDaySerializer, SportWeekSerializer, SportSessionSerializer
from sport.stats import SportStats
from helpers import date_to_week


class SessionManage(RetrieveUpdateDestroyAPIView):
    """
    Fully manage a sport session
    """
    serializer_class = SportSessionSerializer

    def get_queryset(self):
        # TODO: support access rights
        return SportSession.objects.filter(
            day__week__user=self.request.user,
        )

    def perform_update(self, serializer):
        """
        Do not allow updating day
        """
        serializer.save(day=serializer.instance.day)


class SessionCreate(CreateAPIView):
    """
    Fully manage a sport session
    """
    serializer_class = SportSessionSerializer

    def perform_create(self, serializer):
        """
        Create needed hierarchy for session when needed
        """

        # Get date to create hierarchy
        date = serializer.validated_data['day']['date']
        w, year = date_to_week(date)
        week, _ = SportWeek.objects.get_or_create(year=year, week=w, user=self.request.user)
        day, _ = SportDay.objects.get_or_create(week=week, date=date)

        # Create new session on this day
        serializer.save(day=day)


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
