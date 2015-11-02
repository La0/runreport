from users.views.mixins import ProfilePrivacyMixin
from sport.views import RunCalendarYear, RunCalendar, RunCalendarDay, WeeklyReport, ExportMonth
from datetime import date, timedelta
from django.core.exceptions import PermissionDenied

class AthleteCalendarMixin(ProfilePrivacyMixin):
  rights_needed = ('calendar', )

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageweek' : 'user-calendar-week',
      'pageday' : 'user-calendar-day',
    }

  def get_context_data(self, *args, **kwargs):
    context = super(AthleteCalendarMixin, self).get_context_data(*args, **kwargs)
    context['fog'] = self.get_days_in_fog()
    return context

  def get_days_in_fog(self):
    '''
    Hide some days when a club has not
    paid for its athletes
    '''

    # Only for trainers
    if 'trainer' not in self.privacy:
        return None

    # Only for clubs without full access
    access = [m.club.has_full_access for m in self.member.memberships.filter(trainers=self.request.user)]
    if True in access:
        return None

    today = date.today()
    days = range(-15, 7)
    return [today + timedelta(days=d) for d in days]

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
    fog = self.get_days_in_fog()
    if fog and self.day not in fog:
      raise PermissionDenied

    return out

class AthleteExportMonth(ProfilePrivacyMixin, ExportMonth):
  rights_needed = ('trainer', )
