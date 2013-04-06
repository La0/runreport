from django.views.generic import DetailView
from django.views.generic.dates import WeekArchiveView
from mixins import ClubMixin
from run.views.mixins import CurrentWeekMixin
from run.models import RunReport
from helpers import week_to_date

class ClubMembers(CurrentWeekMixin, ClubMixin, WeekArchiveView):
  template_name = 'club/members.html'
  context_object_name = 'reports'

  def get_dated_items(self):
    self.members = self.club.members.all().order_by('first_name')

    # Load reports and week dates
    year = self.get_year()
    week = self.get_week()
    reports = RunReport.objects.filter(user=self.members, year=year, week=week)
    dates = [week_to_date(year, week, d) for d in (1,2,3,4,5,6,0)]

    # Index reports by user
    reports_users = {}
    for r in reports:
      reports_users[r.user.id] = r

    context = {
      'dates' : dates,
      'members' : self.members,
    }
    return (dates, reports_users, context)

class ClubMember(ClubMixin, DetailView):
  template_name = 'club/member.html'
  context_object_name = 'member'
  
  def get_object(self):
    return self.club.members.get(username=self.kwargs['username'])
