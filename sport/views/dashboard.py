from django.views.generic import TemplateView
from sport.stats import StatsWeek
from sport.models import SportSession
from helpers import date_to_day
from datetime import timedelta, date

class DashBoardView(TemplateView):
  '''
  Dashboard of user activity
  '''
  template_name = 'sport/dashboard.html'


  def get(self, request, *args, **kwargs):
    # Render minimal response
    # for visitors
    if not request.user.is_authenticated():
      self.object_list = []
      self.template_name = "landing/index.html" # Use landing page
      return self.render_to_response({})

    return super(DashBoardView, self).get(request, *args, **kwargs)


  def get_context_data(self):
    context = super(DashBoardView, self).get_context_data()
    self.today = date.today()
    context['today'] = self.today
    context.update(self.load_weeks())
    context.update(self.load_sessions())
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
    for w in range(-weeks_past * 7, weeks_future * 7, 7):
      day = start + timedelta(days=w)
      week, year = int(day.strftime('%W')), day.year
      if w > 0:
        state = 'future'
      elif w < 0:
        state = 'past'
      else:
        state = 'current'
      weeks.append({
        'date' : day,
        'year' : year,
        'week' : week,
        'stats' : StatsWeek(self.request.user, year, week),
        'state' : state,
      })

    return {
      'weeks' : weeks,
    }

  def load_sessions(self):
    '''
    Load sessions close to today
    '''
    filters = {
      'day__week__user' : self.request.user,
      'day__date__gte' : self.today - timedelta(days=7),
      'day__date__lte' : self.today + timedelta(days=4),
    }
    sessions = SportSession.objects.filter(**filters)
    sessions = sessions.select_related('day', 'track')
    sessions = sessions.order_by('-day__date')

    return {
      'sessions' : sessions,
    }
