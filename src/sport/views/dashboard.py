from django.views.generic import TemplateView, View
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from sport.stats import StatsWeek
from sport.models import SportSession
from sport.vma import VmaCalc
from club.models import ClubMembership
from runreport.mixins import LoginRequired, JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML
from helpers import date_to_day
from datetime import timedelta, date
from collections import OrderedDict

class DashBoardView(TemplateView):
  '''
  Dashboard of user activity
  '''
  mode = 'athlete' # athlete | trainer

  def get(self, request, *args, **kwargs):
    # Render minimal response
    # for visitors
    if not request.user.is_authenticated():
      self.object_list = []
      self.template_name = "landing/index.html" # Use landing page
      return self.render_to_response({})

    # Detect mode
    trainer_memberships = request.user.memberships.filter(role='trainer')
    self.is_trainer = trainer_memberships.exists()
    self.mode = self.kwargs.get('type', self.is_trainer and 'trainer' or 'athlete')

    # Check trainer mode is accessible
    self.clubs = None
    self.club = None
    if self.mode == 'trainer':
      if not self.is_trainer:
        raise PermissionDenied

      # Load available clubs
      clubs = trainer_memberships.values_list('club_id', flat=True)
      self.clubs = request.user.club_set.filter(pk__in=clubs)

      # Pick current club
      if self.kwargs.get('club'):
        self.club = self.clubs.get(slug=self.kwargs['club'])
      else:
        self.club = self.clubs.first()

    return super(DashBoardView, self).get(request, *args, **kwargs)

  def get_template_names(self):
    # Get template according to user type
    if not self.request.user.is_authenticated():
      return ('landing/index.html', )

    return ('dashboard/%s.html' % self.mode, )

  def get_context_data(self, *args, **kwargs):
    context = super(DashBoardView, self).get_context_data(*args, **kwargs)

    # Common context
    self.today = date.today()
    context['today'] = self.today
    context['mode'] = self.mode
    context['is_trainer'] = self.is_trainer

    # Load athlete datas
    if self.mode == 'athlete':
      context.update(self.load_weeks())
      context.update(self.load_races())
      context.update(self.load_sessions())
      context.update(self.load_friends_sessions())
      context.update(self.load_vma())
      context.update(self.load_demo(self.mode))

    # Load trainer data
    if self.mode == 'trainer':
      context['memberships'] = self.request.user.memberships.filter(role='trainer')
      context['clubs'] = self.clubs
      context['club'] = self.club
      context.update(self.load_prospects())
      context.update(self.load_trained_sessions())
      context.update(self.load_trained_races())
      context.update(self.load_plans())
      context.update(self.load_demo(self.mode))

    return context

  def load_weeks(self):
    '''
    Load previous weeks
    '''
    # List 12 previous weeks
    start = date_to_day(self.today)
    weeks_future = 3
    weeks_past = 6
    weeks = []
    empty = True # Check if there are some data to display
    for w in range(-weeks_past * 7, weeks_future * 7, 7):
      day = start + timedelta(days=w)
      week, year = int(day.strftime('%W')), day.year
      if w > 0:
        state = 'future'
      elif w < 0:
        state = 'past'
      else:
        state = 'current'
      st = StatsWeek(self.request.user, year, week)
      weeks.append({
        'date' : day,
        'year' : year,
        'week' : week,
        'stats' : st,
        'state' : state,
      })
      if empty:
        empty = st.data is None

    return {
      'weeks_empty' : empty,
      'weeks' : weeks,
    }

  def load_sessions(self):
    '''
    Load sessions close to today
    '''
    filters = {
      'type' : 'training',
      'day__week__user' : self.request.user,
      'day__date__gte' : self.today,
      'day__date__lte' : self.today + timedelta(days=10),
    }
    sessions = SportSession.objects.filter(**filters)
    sessions = sessions.select_related('day', 'track')
    sessions = sessions.order_by('day__date')

    return {
      'sessions' : sessions,
    }

  def load_races(self):
    '''
    Load all future races
    '''
    filters = {
      'day__week__user' : self.request.user,
      'day__date__gte' : self.today,
      'type' : 'race',
    }
    races = SportSession.objects.filter(**filters)
    races = races.select_related('day', 'track')
    races = races.order_by('day__date')

    return {
      'races' : races,
    }

  def load_friends_sessions(self):
    '''
    Load athlete friends sessions
    * close to today
    * grouped by athletes
    '''
    filters = {
      'day__week__user__in' : self.request.user.friends.all(),
      'day__date__gte' : self.today,
      'day__date__lte' : self.today + timedelta(days=30),
    }
    sessions = SportSession.objects.filter(**filters)
    sessions = sessions.select_related('day', 'track')
    sessions = sessions.order_by('day__week__user__first_name', 'day__date')

    # Group
    friends = OrderedDict()
    for s in sessions:
      user = s.day.week.user
      if user.pk not in friends:
        friends[user.pk] = {
          'user' : user,
          'sessions' : [],
        }
      friends[user.pk]['sessions'].append(s)

    return {
      'friends' : friends,
    }

  def load_prospects(self):
    '''
    Load prospects in all the clubs of manager
    '''
    filters = {
      'club__manager' : self.request.user,
      'club' : self.club,
      'role' : 'prospect',
    }
    prospects = ClubMembership.objects.filter(**filters)

    return {
      'prospects' : prospects,
    }

  def load_trained_sessions(self):
    '''
    Load past sessions close to today
    for all the trainer's athletes
    Grouped by dates
    '''
    filters = {
      'day__date__gte' : self.today - timedelta(days=7),
      'day__date__lte' : self.today,
      'day__week__user__memberships__trainers' : self.request.user,
      'day__week__user__memberships__role__in' : ('trainer', 'athlete'),
    }
    sessions = SportSession.objects.filter(**filters)
    sessions = sessions.select_related('day', 'track')
    sessions = sessions.exclude(day__week__user=self.request.user)
    sessions = sessions.order_by('-day__date')

    # Group by dates
    groups = OrderedDict()
    for s in sessions:
      d = s.day.date
      if d not in groups:
        groups[d] = []
      groups[d].append(s)

    return {
      'sessions' : groups,
    }

  def load_trained_races(self):
    '''
    Load future races
    for all the trainer's athletes
    '''
    filters = {
      'type' : 'race',
      'day__date__gte' : self.today,
      'day__date__lte' : self.today + timedelta(days=60),
      'day__week__user__memberships__trainers' : self.request.user,
      'day__week__user__memberships__role__in' : ('trainer', 'athlete'),
    }
    races = SportSession.objects.filter(**filters)
    races = races.select_related('day', 'track')
    races = races.exclude(day__week__user=self.request.user)
    races = races.order_by('day__date')
    races = races[0:15]

    return {
      'races' : races,
    }

  def load_vma(self):
    '''
    Load some vma speeds for current user
    '''
    vma = self.request.user.vma
    if not vma:
      return {
        'vma': None,
      }

    # Calc some times
    vc = VmaCalc(vma)
    paces = (60, 80, 90, 100)
    distances = (100, 200, 400, 500, 1000)
    speeds = []
    for i,d in enumerate(distances):
      speeds.append([])
      for p in paces:
        speeds[i].append(vc.get_time(p, d))

    return {
      'vma' : {
        'paces' : paces,
        'distances' : distances,
        'speeds' : speeds,
      }
    }

  def load_plans(self):
    '''
    Load last created plans
    '''
    plans = self.request.user.plans.order_by('-created')[0:3]
    return {
      'plans' : plans,
    }

  def load_demo(self, mode):
    '''
    Load demo steps
    '''
    active = self.request.user.check_demo_steps(mode)
    if active is None:
      return {}

    # Build trainer demo steps
    if mode == 'trainer':
      if self.club.manager == self.request.user:
        demo = [
          {
            'name' : 'invite',
            'url' : reverse('club-manage', args=(self.club.slug, )) + '#invites',
            'title' : _('Invite an athlete'),
          },
        ]
      else:
        demo = []
      demo += [
        {
          'name' : 'plan',
          'url' : settings.PLANS_URL,
          'title' : _('Create a training plan'),
        },
        {
          'name' : 'plan_applied',
          'url' : settings.PLANS_URL,
          'title' : _('Send a plan to your athletes'),
        },
        {
          'name' : 'comment',
          'url' : None,
          'title' : _('Leave a comment to one of your athlete session'),
        },
      ]
    elif mode == 'athlete':
      demo = [
        {
          'name' : 'session',
          'url' : reverse('report-current'),
          'title' : _('Create your first sport session'),
        },
        {
          'name' : 'join',
          'url' : reverse('club-list'),
          'title' : _('Join a club'),
        },
        {
          'name' : 'friends',
          'url' : reverse('friends'),
          'title' : _('Add some friends to see their sessions'),
        },
        {
          'name' : 'gps',
          'url' : reverse('track-providers'),
          'title' : _('Sync your GPS watch or app'),
        },
        {
          'name' : 'comment',
          'url' : None,
          'title' : _('Add a comment on a session'),
        },
      ]

    # Apply active steps
    for step in demo:
      step['active'] = active.get(step['name'], False)

    return {
      'demo' : demo,
    }



class DemoSkipView(LoginRequired, View, JsonResponseMixin):
  '''
  Allow skipping some demo steps
  Could be in an api, but not critical
  '''

  def post(self, request, *args, **kwargs):

    # Check step/mode
    step = request.POST.get('step')
    mode = request.POST.get('mode')
    if not step or not mode:
      raise Exception('Missing mode or step')

    # Update steps
    request.user.check_demo_steps(mode, force_steps=(step, ))

    # Reload
    self.json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, ]

    return self.render_to_response({})
