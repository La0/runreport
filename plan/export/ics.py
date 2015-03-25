from __future__ import absolute_import
from django.contrib.sites.models import get_current_site
from ics import Calendar, Event
from datetime import datetime, timedelta


class PlanIcsExporter(object):

  def __init__(self, plan):
    self.site = get_current_site(None)
    self.plan = plan

  def build_calendar(self, stream=None):
    '''
    Build calendar from sessions
    '''

    cal = Calendar()
    # Add sessions and dates to lines
    for week_pos in range(0, self.plan.weeks_nb):
      week = []

      for day_pos in range(0, 7):
        sessions = []

        date = self.plan.calc_date(week_pos, day_pos)

        # Render sessions using html template
        for session in self.plan.sessions.filter(week=week_pos, day=day_pos):
          e = Event()
          e.name = session.name

          e.description = session.sport.name + " - " + session.type + "\n"
          # [TODO] check hour planned for training
          e.begin = datetime.combine(date,datetime.min.time()) + timedelta(hours=19)
          if session.distance is not None:
            e.description += "Distance: %f \n " % session.distance
          if session.time is not None:
            e.description += "Duration: %s \n " % session.time
            e.duration = session.time
          else:
            e.duration = timedelta(hours=2)

          cal.events.append(e)

        week.append(sessions or '')

    stream.write(str(cal))
