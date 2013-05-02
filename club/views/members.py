from django.views.generic import DetailView, ListView
from django.http import Http404
from django.views.generic.dates import WeekArchiveView
from django.contrib.auth.models import User
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
    from django.db.models import Max
    members = members.annotate(max_report_date=Max('runreport__sessions__date'))

    return {
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

    # Super inefficient.
    # TODO: We should'nt have any empty RunReport to begin with...
    for r in reports:
      r.nb_sessions = r.sessions.exclude(name__isnull=True, comment__isnull=True).count()
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
      sessions = report.sessions.all().order_by('date')
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
