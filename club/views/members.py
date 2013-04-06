from django.views.generic import DetailView
from django.views.generic.dates import WeekArchiveView
from mixins import ClubMixin
from run.views.mixins import CurrentWeekMixin, WeekPaginator
from run.models import RunReport
from helpers import week_to_date

class ClubMembers(CurrentWeekMixin, ClubMixin, WeekPaginator, WeekArchiveView):
  template_name = 'club/members.html'
  context_object_name = 'reports'
  weeks_around_nb = 3

  def get_dated_items(self):

    # Load members, reports and week dates
    year = self.get_year()
    week = self.get_week()
    dates = [week_to_date(year, week, d) for d in (1,2,3,4,5,6,0)]
    self.date = dates[0]
    self.check_limits() # Load & check date limits
    self.members = self.club.members.all().order_by('first_name')
    reports = RunReport.objects.filter(user=self.members, year=year, week=week)

    # Index reports by user
    reports_users = {}
    for r in reports:
      reports_users[r.user.id] = r

    context = {
      'dates' : dates,
      'members' : self.members,
      'pagename' : 'club-week',
      'pageargs' : [self.club.slug,],
    }

    # Pagination
    context.update(self.paginate(self.date, self.min_date, self.max_date))

    return (dates, reports_users, context)

class ClubMember(ClubMixin, DetailView):
  template_name = 'club/member.html'
  context_object_name = 'member'
  
  def get_object(self):
    return self.club.members.get(username=self.kwargs['username'])
