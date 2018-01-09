from users.views.mixins import ProfilePrivacyMixin
from sport.views import RunCalendarYear, RunCalendar, RunCalendarDay, WeeklyReport, ExportMonth
from django.core.exceptions import PermissionDenied


class AthleteCalendarMixin(ProfilePrivacyMixin):
    rights_needed = ('calendar', )
    club_fog = None

    def get_links(self):
        return {
            'pageargs': [self.member.username, ],
            'pageyear': 'user-calendar-year',
            'pagemonth': 'user-calendar-month',
            'pageweek': 'user-calendar-week',
            'pageday': 'user-calendar-day',
        }

    def get_context_data(self, *args, **kwargs):
        context = super(
            AthleteCalendarMixin,
            self).get_context_data(
            *
            args,
            **kwargs)
        context['fog'] = self.get_fog_limit()
        context['club_fog'] = self.club_fog
        return context

    def get_fog_limit(self):
        '''
        When club is not in full access
        Days AFTER this limit are hidden
        '''

        # Only for trainers
        if 'trainer' not in self.privacy:
            return None

        # Only for clubs without full access
        memberships = self.member.memberships.filter(
            trainers=self.request.user)
        for m in memberships:
            if m.club.has_full_access:
                continue

            self.club_fog = m.club
            return m.club.current_period.end.date()

        return None


class AthleteCalendarYear(AthleteCalendarMixin, RunCalendarYear):
    pass


class AthleteCalendarMonth(AthleteCalendarMixin, RunCalendar):
    pass


class AthleteCalendarWeek(AthleteCalendarMixin, WeeklyReport):
    pass


class AthleteCalendarDay(AthleteCalendarMixin, RunCalendarDay):

    def get_object(self, *args, **kwargs):
        out = super(AthleteCalendarDay, self).get_object(*args, **kwargs)

        # Check current day is not in fog
        fog = self.get_fog_limit()
        if fog and self.day >= fog:
            raise PermissionDenied

        return out


class AthleteExportMonth(ProfilePrivacyMixin, ExportMonth):
    rights_needed = ('trainer', )
