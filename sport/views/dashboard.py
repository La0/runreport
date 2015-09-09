from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from sport.stats import StatsWeek
from sport.models import SportSession
from sport.vma import VmaCalc
from club.models import ClubMembership
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
    self.is_trainer = request.user.is_trainer
    self.mode = self.kwargs.get('type', self.is_trainer and 'trainer' or 'athlete')

    # Check trainer mode is accessible
    if self.mode == 'trainer' and not self.is_trainer:
      raise PermissionDenied

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

    # Load trainer data
    if self.mode == 'trainer':
      context['memberships'] = self.request.user.memberships.filter(role='trainer')
      context.update(self.load_prospects())
      context.update(self.load_trained_sessions())
      context.update(self.load_trained_races())
      context.update(self.load_plans())

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
