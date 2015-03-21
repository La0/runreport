from datetime import datetime, timedelta, date
from coach.mixins import JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from helpers import week_to_date, date_to_day, date_to_week
from sport.models import SportWeek, SportDay, SportSession, SESSION_TYPES, RaceCategory
from sport.forms import SportSessionForm
from django.db.models import Sum, Count

class CurrentWeekMixin(object):
  '''
  Gives the current year & week or
  uses the one from kwargs (url)
  '''
  context_object_name = 'report'
  _today = None
  _week = None
  _year = None

  def __init__(self):
    self._today = date.today()
    self._week, self._year = date_to_week(date.today())

  def get_year(self):
    return int(self.kwargs.get('year', self._year))

  def get_week(self):
    return int(self.kwargs.get('week', self._week))

  def get_object(self):
    '''
    Load existing week
    or create a new week in limits
    '''
    self.date = week_to_date(self.get_year(), week=self.get_week())
    try:
      week = SportWeek.objects.get(year=self.get_year(), week=self.get_week(), user=self.get_user())
      self.check_limits(False) # no checks for existing
    except SportWeek.DoesNotExist, e:
      week = SportWeek.objects.create(year=self.get_year(), week=self.get_week(), user=self.get_user())
      self.check_limits(False) # don't create any future week

    return week

  def check_limits(self, check=True):
    # Min date is oldest user sport week
    # or first day of current year by default
    oldest = SportDay.objects.filter(week__user=self.request.user).order_by('date').first()
    if oldest:
      self.min_date = oldest.week.get_date_start()
    else:
      self.min_date = date(self._today.year, 1, 1)

    # Load min & max date
    self.max_date = date_to_day(self._today)
    if not check:
      return

    # Check we are not in past or future
    if self.date > self._today:
      raise Http404('In the future.')

  def get_user(self):
    # By default, use connected user
    return self.request.user

  def get_links(self):
    return {
      'pageargs' : [],
      'pagemonth' : 'report-month',
      'pageweek' : 'report-week',
      'pageday' : 'report-day',
    }

  def get_privacy(self):
    # Add privacy for current visitor
    week = self.get_object()
    return {
      'privacy' : week.user.get_privacy_rights(self.request.user),
    }

  def get_context_data(self, *args, **kwargs):
    context = super(CurrentWeekMixin, self).get_context_data(*args, **kwargs)
    context.update(self.get_links())
    context.update(self.get_privacy())
    return context

class WeekPaginator(object):
  '''
  Paginates using weeks urls around a date
  '''
  weeks = []
  weeks_around_nb = 2

  def get_context_data(self, *args, **kwargs):
    # Add pagination to context
    context = super(WeekPaginator, self).get_context_data(*args, **kwargs)

    # Pagination
    context.update(self.paginate(self.date, self.min_date, self.max_date))

    return context


  # Build self.weeks for pagination
  def _build_week(self, week_date, page_date):
    return {
      'display'  : 'week',
      'start' : week_date,
      'end'   : week_date + timedelta(days=6),
      'current' : (week_date == page_date),
      'week'  : int(week_date.strftime('%W')),
      'year'  : week_date.year,
    }

  def paginate(self, page_date, min_date, max_date):
    self.weeks = []
    # Add first week
    self.weeks.append(self._build_week(min_date, page_date))

    # Add viewed week and X on each side
    weeks_around = range(-self.weeks_around_nb, self.weeks_around_nb+1)
    for i in weeks_around:
      dt = page_date + timedelta(days=i*7)
      if dt <= min_date or dt >= max_date:
        continue
      if i == min(weeks_around):
        self.weeks.append({'display' : 'spacer'})
      self.weeks.append(self._build_week(dt, page_date))
      if i == max(weeks_around):
        self.weeks.append({'display' : 'spacer'})

    # Add current week (last)
    self.weeks.append(self._build_week(max_date, page_date))

    # Search current
    current_pos = 0
    i = 0
    for w in self.weeks:
      if w['display'] == 'week' and w['start'] == page_date:
        current_pos = i
      i += 1

    useful_weeks = [w for w in self.weeks if w['display'] == 'week'] # skip spacers
    week_previous = current_pos - 1 > 0 and useful_weeks[current_pos - 1] or None
    week_next = current_pos + 1 < len(useful_weeks) and useful_weeks[current_pos + 1] or None

    # TODO: integrate to get_context_data
    return {
      'weeks' : self.weeks,
      'week_previous' : week_previous,
      'week_next' : week_next,
    }

class CalendarDay(object):
  '''
  Load a SportDay from a date in url
  '''
  month_format = '%M'
  context_object_name = 'session'

  def get_object(self):

    # Load day, report and eventual session
    self.day = date(int(self.get_year()), int(self.get_month()), int(self.get_day()))
    week, year = date_to_week(self.day)
    self.week, created = SportWeek.objects.get_or_create(user=self.get_user(), year=year, week=week)
    try:
      self.object = SportDay.objects.get(week=self.week, date=self.day)
    except:
      self.object = SportDay(week=self.week, date=self.day)
    return self.object

  def get_context_data(self, **kwargs):
    context = super(CalendarDay, self).get_context_data(**kwargs)
    context['day_date'] = self.day
    context['report'] = self.week
    context['session_types'] = SESSION_TYPES
    context['day'] = self.object
    context.update(self.get_links())
    return context

  def get_user(self):
    # By default, use connected user
    return self.request.user

  def get_links(self):
    return {
      'pageargs' : [],
      'pagemonth' : 'report-month',
      'pageweek' : 'report-week',
      'pageday' : 'report-day',
    }

class CalendarSession(CalendarDay):

  def get_object(self):
    super(CalendarSession, self).get_object()

    session_id = None
    if 'session' in self.kwargs:
      # Check get for session id
      session_id = self.kwargs['session']
    elif self.request.method == 'POST' and 'session' in self.request.POST:
      # Check raw post for session id
      session_id = self.request.POST['session']

    # Init a session
    if session_id:
      self.session = SportSession.objects.get(pk=session_id, day__week__user=self.request.user)
    else:
      self.session = SportSession(sport=self.request.user.default_sport, day=self.object)

    return self.session

  def get_context_data(self, *args, **kwargs):
    context = super(CalendarSession, self).get_context_data(*args, **kwargs)
    context['session'] = self.session
    return context

class SportSessionForms(object):

  def get_sessions_forms(self, date, day=None):
    '''
    Build SportSessionForm instances for a day
    '''
    if self.get_user() != self.request.user:
      return []

    default_sport = self.request.user.default_sport
    post_data = None # No need for POST, as the action is on another url

    # Load existing sessions
    if day and day.sessions.count() > 0:
      sessions = day.sessions.all().order_by('created')
      sessions = sessions.prefetch_related('sport', 'track', 'plan_session', 'plan_session__plan_session__plan')
      return [SportSessionForm(default_sport, date, post_data, instance=s) for s in sessions]

    # At least one empty form
    instance = SportSession(sport=default_sport)
    return [SportSessionForm(default_sport, date, post_data, instance=instance) ]


class AthleteRaces(object):

  def get_context_data(self, *args, **kwargs):
    '''
    Usable in club or direct user context
    '''
    context = super(AthleteRaces, self).get_context_data(*args, **kwargs)
    user = hasattr(self, 'member') and self.member or self.request.user
    context.update(self.get_races(user))
    return context

  def get_races(self, user):

    # List races days
    race_days = SportDay.objects.filter(week__user=user, sessions__type='race')
    future_races = race_days.filter(date__gt=date.today()).order_by('date')
    past_races = race_days.filter(date__lte=date.today())

    # Extract the categories from past_races
    cat_ids = [r['sessions__race_category'] for r in past_races.values('sessions__race_category').distinct() if r['sessions__race_category']]
    categories = dict([(c.id, c) for c in RaceCategory.objects.filter(pk__in=cat_ids).order_by('name')])

    # Sum sessions time & distance per race
    past_races = past_races.annotate(time_total=Sum('sessions__time'), distance_total=Sum('sessions__distance'), nb_sessions=Count('sessions')).order_by('time_total')

    '''
    for c in categories:
      races[c.id] = past_races.filter(sessions__race_category=c).order_by('time_total')
    '''

    # Categorize races
    # Smartwer way : the past_races query is evaluated here
    races = {}
    for r in past_races:
      for c in r.sessions.filter(type='race').values('race_category').distinct():
        cat_id = c['race_category']
        cat = categories[cat_id]
        if cat_id not in races:
          races[cat_id] = []
        races[cat_id].append(r)

    return {
      'future_races' : future_races,
      'races' : races,
      'categories' : categories,
    }
