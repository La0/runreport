from users.views.mixins import ProfilePrivacyMixin
from sport.views import RunCalendarYear, RunCalendar, RunCalendarDay, WeeklyReport

class AthleteCalendarYear(ProfilePrivacyMixin, RunCalendarYear):
  rights_needed = ('profile', 'calendar')

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageday' : 'user-calendar-day',
    }

class AthleteCalendarMonth(ProfilePrivacyMixin, RunCalendar):
  rights_needed = ('profile', 'calendar')

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageday' : 'user-calendar-day',
    }


class AthleteCalendarWeek(ProfilePrivacyMixin, WeeklyReport):
  rights_needed = ('profile', 'calendar')

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pagemonth' : 'user-calendar-month',
      'pageweek' : 'user-calendar-week',
      'pageday' : 'user-calendar-day',
    }

class AthleteCalendarDay(ProfilePrivacyMixin, RunCalendarDay):
  rights_needed = ('profile', 'calendar')

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pagemonth' : 'user-calendar-month',
      'pageweek' : 'user-calendar-week',
      'pageday' : 'user-calendar-day',
    }
