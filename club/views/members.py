from django.views.generic import DetailView, ListView
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.http import Http404
from django.views.generic.dates import WeekArchiveView
from django.contrib.auth.models import User
from django.db.models import Count, Max
from mixins import ClubMixin
from run.views.mixins import CurrentWeekMixin, WeekPaginator
from run.models import RunReport
from club.models import ClubMembership
from helpers import week_to_date
from club.forms import ClubMembershipForm
from datetime import date

class ClubMembers(ClubMixin, ListView):
  template_name = 'club/members.html'
  model = User

  def load_members(self):
    # Filter members
    default_type = 'athletes'
    filters = {
      'all' : None,
      'athletes' : {
        'memberships__role' : 'athlete',
        'memberships__trainers' : self.request.user,
      },
      'archives' : {
        'memberships__role' : 'archive',
      }
    }

    # Load members, sorted by name
    f = filters.get(self.kwargs.get('type', default_type), None)
    members = self.club.members.prefetch_related('memberships')
    if f: # Don't use ternary !
      members = members.filter(**f)

    # Add last RunReport date, as week & year
    members = members.annotate(max_report_date=Max('runreport__sessions__date'))
    members = members.annotate(nb_sessions=Count('runreport__sessions'))

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

    # Apply club membership
    for m in members:
      m.membership = m.memberships.get(club=self.club)

    return {
      'type' : self.kwargs.get('type', default_type),
      'sort' : self.kwargs.get('sort', default_sort),
      'members' : members,
    }

  def get_context_data(self, **kwargs):
    context = super(ClubMembers, self).get_context_data(**kwargs)
    context.update(self.load_members())
    context['today'] = date.today()
    return context

class ClubMember(ClubMixin, DetailView):
  template_name = 'club/member.html'
  context_object_name = 'membership'
  model = ClubMembership
  
  def get_context_data(self, **kwargs):
    context = super(ClubMember, self).get_context_data(**kwargs)
    context['membership'] = self.membership
    context['member'] = self.member
    return context

  def get_object(self):
    self.object = self.membership # needed for inherited classes
    return self.object

class ClubMemberRole(ClubMixin, ModelFormMixin, ProcessFormView, DetailView):
  template_name = 'club/role.html'
  context_object_name = 'membership'
  model = ClubMembership
  form_class = ClubMembershipForm
  
  def get_context_data(self, **kwargs):
    context = super(ClubMemberRole, self).get_context_data(**kwargs)
    context['membership'] = self.membership
    context['member'] = self.member
    context['stats'] = self.stats
    return context

  def get_form(self, form_class):
    self.role_original = self.membership.role
    # Load object before form init
    if not hasattr(self, 'object'):
      self.get_object()
    return super(ClubMemberRole, self).get_form(form_class)

  def form_valid(self, form):
    try:
      membership = form.save(commit=False)
      if self.role_original == membership.role:
        raise Exception("Same role. No update.")

      # Check club has a place available
      if membership.role != 'archive':
        stat = [s for s in self.stats if membership.role == s['type']][0]
        if stat['diff'] <= 0:
          raise Exception('No place available')
      membership.save()
    except Exception, e:
      raise Exception("Failed to save")
    return self.render_to_response(self.get_context_data(**{'form' : form}))

  def form_invalid(self, form):
    raise Exception("Invalid form")

  def get_object(self):
    self.stats = self.club.load_stats()
    self.object = self.membership # needed for inherited classes
    return self.object

class ClubMemberWeek(CurrentWeekMixin, ClubMixin, WeekPaginator, WeekArchiveView):
  template_name = 'club/member.week.html'
  context_object_name = 'sessions'

  def get_dated_items(self):

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
