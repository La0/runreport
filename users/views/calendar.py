from users.views.mixins import ProfilePrivacyMixin
from sport.views import RunCalendarYear, RunCalendar, RunCalendarDay, WeeklyReport, SportSessionView

class AthleteCalendarMixin(ProfilePrivacyMixin):
  rights_needed = ('profile', 'calendar')

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageweek' : 'user-calendar-week',
      'pageday' : 'user-calendar-day',
    }

class AthleteCalendarYear(AthleteCalendarMixin, RunCalendarYear):
  pass

class AthleteCalendarMonth(AthleteCalendarMixin, RunCalendar):
  pass

class AthleteCalendarWeek(AthleteCalendarMixin, WeeklyReport):
  pass

class AthleteCalendarDay(AthleteCalendarMixin, RunCalendarDay):
  pass
