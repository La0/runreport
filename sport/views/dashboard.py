from django.views.generic import TemplateView


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
    context.update(self.load_weeks())
    return context

  def load_weeks(self):
    '''
    Load previous weeks
    '''
    from sport.stats import StatsWeek
    from helpers import date_to_day
    from datetime import timedelta, date

    # List 12 previous weeks
    start = date_to_day(date.today())
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
