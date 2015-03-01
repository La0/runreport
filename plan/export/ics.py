from __future__ import absolute_import
from django.contrib.sites.models import get_current_site
from django.utils import formats
from helpers import week_to_date
from ics import Calendar, Event
from StringIO import StringIO
from datetime import datetime, timedelta


class PlanIcsExporter(object):

  def __init__(self, plan):
    self.site = get_current_site(None)
    self.plan = plan

  def build_calendar(self, stream=None):
    '''
    Build lines content from sessions
    '''

    cal = Calendar()
    # Add sessions and dates to lines
    for week_pos in range(0, self.plan.get_weeks_nb()):
      dates = []
      week = []

      for day_pos in range(0, 7):
        sessions = []

        # Render date
        date = self.plan.calc_date(week_pos, day_pos)
#        if date:
#          date_fmt = formats.date_format(date, "SHORT_DATE_FORMAT")
#          dates.append(Paragraph(date_fmt, self.dateStyle))

        # Render sessions using html template
        for session in self.plan.sessions.filter(week=week_pos, day=day_pos):
          e = Event()
          e.name = session.name

          e.description = session.sport.name + " - " + session.type
          # [TODO] check hour planned for training
          e.begin = datetime.combine(date,datetime.min.time()) + timedelta(hours=19)
          if session.distance is not None:
            e.description += " \n " + session.distance
          if session.time is not None:
            e.description += " \n " + session.time
            e.duration = session.time
          else:
            e.duration = timedelta(hours=2)


          cal.events.append(e)

        week.append(sessions or '')


    stream.write(str(cal))

     # if isinstance(stream, StringIO):
      #  output = stream.getvalue()
       # stream.close()
        #return output