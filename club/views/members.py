from django.views.generic import DetailView, ListView
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.http import Http404
from django.views.generic.dates import WeekArchiveView
from users.models import Athlete
from django.db.models import Count, Max
from mixins import ClubMixin, ClubManagerMixin
from sport.views.mixins import CurrentWeekMixin, WeekPaginator
from sport.models import SportWeek
from club.models import ClubMembership
from helpers import week_to_date
from club.forms import ClubMembershipForm
from datetime import date
from coach.mixins import JsonResponseMixin, JSON_STATUS_ERROR

class ClubMembers(ClubMixin, ListView):
  template_name = 'club/members.html'
  model = Athlete

  def load_members(self):
    # Filter members
    default_type = 'athletes'
    filters = {
      'all' : None,
      'athletes' : {
        'memberships__role' : 'athlete',
        'memberships__trainers' : self.request.user,
      },
      'staff' : {
        'memberships__role' : 'staff',
      },
      'prospects' : {
        'memberships__role' : 'prospect',
      },
      'archives' : {
        'memberships__role' : 'archive',
      }
    }

    # Remove filters for non manager
    if self.request.user != self.club.manager and not self.request.user.is_staff:
      del filters['all']
      del filters['staff']
      del filters['prospects']
      del filters['archives']

    # Load members, sorted by name
    asked_type = self.kwargs.get('type', default_type)
    if asked_type not in filters:
      raise Http404('Invalid type')
    f = filters[asked_type]
    members = self.club.members.prefetch_related('memberships')
    if f: # Don't use ternary !
      f['memberships__club'] = self.club # to avoid listing other club memberships
      members = members.filter(**f)

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

    # Add last SportWeek date, as week & year
    # Enhance query performance by separating annotation
    # then applying manually the results on queryset
    agg = members.values('pk').annotate(max_date=Max('sportweek__days__date'), nb=Count('sportweek__days'))
    agg = dict((a['pk'], (a['max_date'], a['nb'])) for a in agg)
    for m in members:
      m.max_report_date, m.sessions_count = agg[m.pk]

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

class ClubMemberRole(JsonResponseMixin, ClubManagerMixin, ModelFormMixin, ProcessFormView, DetailView):
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
      membership.trainers = form.cleaned_data['trainers'] # Weird :/

      # Check club has a place available
      if membership.role != 'archive':
        stat = [s for s in self.stats if membership.role == s['type']][0]
        if stat['diff'] <= 0:
          raise Exception('No place available')

      membership.save()

      # Only send mail for new roles
      if self.role_original != membership.role:
        membership.mail_user(self.role_original)
    except Exception, e:
      print str(e)
      raise Exception("Failed to save")

    return self.render_to_response(self.get_context_data(**{'form' : form}))

  def form_invalid(self, form):
    self.json_status = JSON_STATUS_ERROR
    return self.render_to_response(self.get_context_data(**{'form' : form}))

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
      report = SportWeek.objects.get(user=self.member, year=year, week=week)
      sessions = report.get_days_per_date()
      dates = report.get_dates()
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
