from django.views.generic import DetailView, ListView
from django.http import Http404
from django.views.generic.dates import WeekArchiveView
from django.contrib.auth.models import User
from django.db.models import Count, Max
from mixins import ClubMixin
from run.views.mixins import CurrentWeekMixin, WeekPaginator
from run.models import RunReport
from helpers import week_to_date

class ClubMembers(ClubMixin, ListView):
  template_name = 'club/members.html'
  model = User

  def load_members(self):
    # Load members, sorted by name
    members = self.club.members.all().order_by('username')

    # Add last RunReport date, as week & year
    members = members.annotate(max_report_date=Max('runreport__sessions__date'))

    # Sort members
    default_sort = 'username'
    sorts = {
      'name' : default_sort,
      'name-r' : '-username',
      'date' : '-max_report_date',
      'date-r' : 'max_report_date',
    }
    sort = 'sort' in self.kwargs and sorts.get(self.kwargs['sort'], default_sort) or default_sort
    members = members.order_by(sort)

    return {
      'sort' : self.kwargs.get('sort', default_sort),
      'members' : members,
    }

  def get_context_data(self, **kwargs):
    context = super(ClubMembers, self).get_context_data(**kwargs)
    context.update(self.load_members())
    return context

class ClubMember(ClubMixin, DetailView):
  template_name = 'club/member.html'
  context_object_name = 'member'
  
  def get_context_data(self, **kwargs):
    context = super(ClubMember, self).get_context_data(**kwargs)
    context.update(self.load_reports(context['member']))
    return context

  def load_reports(self, member):
    reports = RunReport.objects.filter(user=member).order_by('-year', '-week')

    # Add nb of sessions on reports
    reports = reports.annotate(nb_sessions=Count('sessions'))

    return {
      'reports' : reports,
    }

  def get_object(self):
    return self.club.members.get(username=self.kwargs['username'])

class ClubMemberWeek(CurrentWeekMixin, ClubMixin, WeekPaginator, WeekArchiveView):
  template_name = 'club/member.week.html'
  context_object_name = 'sessions'

  def get_dated_items(self):

    # Load user
    try:
      self.member = self.club.members.get(username=self.kwargs['username'])
    except:
      raise Http404("User %s not found" % self.kwargs['username'])

    # Load report & sessions
    year = self.get_year()
    week = self.get_week()
    try:
      report = RunReport.objects.get(user=self.member, year=year, week=week)
      sessions = report.get_dated_sessions()
      dates = report.get_days()
    except:
      report = sessions = dates = None

    context = {
      'year' : year,
      'week' : week,
      'report' : report,
      'member' : self.member,
      'pagename' : 'club-member-week',
      'pageargs' : [self.club.slug, self.member.username],
    }

    # Pagination
    self.date = week_to_date(year, week)
    self.check_limits()
    context.update(self.paginate(self.date, self.min_date, self.max_date))

    return (dates, sessions, context)