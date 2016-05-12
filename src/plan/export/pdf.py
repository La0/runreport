from reportlab.platypus import Table, Paragraph, Frame, Image, PageTemplate, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_CENTER
from reportlab.rl_config import defaultPageSize
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils import formats, translation
from django.conf import settings
from helpers import week_to_date
from datetime import timedelta
from StringIO import StringIO
import os

class PlanPdfExporter(object):
  '''
  Export a plan as pdf
  '''
  plan = None
  site = None
  lines = None

  # Table line dimensions
  row_heights = []

  # Styles
  tableStyle = []
  dateStyle = None
  sessionStyle = None
  titleStyle = None

  # Pages size
  width = 0
  height = 0

  def __init__(self, plan):
    self.site = get_current_site(None)
    self.plan = plan
    self.lines = []
    self.setup_styles()
    self.width = defaultPageSize[0]
    self.height = defaultPageSize[1]
    self.row_heights = [] # reset for celery workers

    # Check language is activated
    if translation.get_language() is None:
      translation.activate(settings.LANGUAGE_CODE)

  def setup_styles(self):
    # Build style sheets
    s1, s2, s3 = getSampleStyleSheet(), getSampleStyleSheet(), getSampleStyleSheet()
    self.sessionStyle, self.dateStyle = s1['Normal'], s2['Normal']
    self.titleStyle = s3['Heading2']
    self.titleStyle.alignment = TA_CENTER
    self.dateStyle.backColor = colors.grey
    self.dateStyle.textColor = colors.white
    self.dateStyle.alignment = TA_CENTER

    # Base table style
    self.tableStyle = [
      # Grid around the table
      ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]

  def add_days(self):
    '''
    Add day names, from monday to sunday
    '''
    days = []
    for i in range(1, 8):
      date = week_to_date(2015, 1, i % 7) # we just need the day name here
      days.append(Paragraph(date.strftime('%A').title(), self.dateStyle))
    self.remove_padding(len(self.lines))
    self.lines.append(days)
    self.row_heights.append(.2*inch)

  def remove_padding(self, line):
    # Remove padding on a line
    self.tableStyle += [
      ('RIGHTPADDING', (0,line), (-1,line), 0),
      ('LEFTPADDING', (0,line), (-1,line), 0),
      ('TOPPADDING', (0,line), (-1,line), 0),
      ('BOTTOMPADDING', (0,line), (-1,line), 0),
    ]

  def build_lines(self):
    '''
    Build lines content from sessions
    '''

    # Add sessions and dates to lines
    for week_pos in range(0, self.plan.weeks_nb):
      dates = []
      week = []

      # No padding for dates
      if self.plan.start:
        self.remove_padding((week_pos * 2) + 1)

      for day_pos in range(0, 7):
        sessions = []

        # Render date
        date = self.plan.calc_date(week_pos, day_pos)
        if date:
          date_fmt = formats.date_format(date, "SHORT_DATE_FORMAT")
          dates.append(Paragraph(date_fmt, self.dateStyle))

        # Render sessions using html template
        sum_distance, sum_time = 0, timedelta()
        for session in self.plan.sessions.filter(week=week_pos, day=day_pos):
          content = '<b><font color=lightsteelblue size=9>{}</font></b> <font size=9>{}</font>'.format(session.sport, session.name)
          para = Paragraph(content, self.sessionStyle)
          sessions.append(para)
          sum_distance += session.distance or 0
          sum_time += session.time or timedelta()

        # Add distance & time summary for this day
        if sum_distance or sum_time:
          content = ' '.join([
            sum_distance and '{} km'.format(sum_distance) or '',
            sum_time and '{}'.format(sum_time) or '',
          ])
          content = '<font size=8 color=darkslateblue>Total: {}</font>'.format(content)
          summary = Paragraph(content, self.sessionStyle)
          sessions.append(summary)

        week.append(sessions or '')

      if dates:
        self.lines.append(dates)
        self.row_heights.append(0.2*inch)
      self.lines.append(week)
      self.row_heights.append(1.1*inch)


  def render(self, stream=None):
    '''
    Render the pdf with current lines & style
    '''
    # Use a buffer when no stream is given
    if stream is None:
      stream = StringIO()

    # Build lines
    self.add_days()
    self.build_lines()

    # Canvas is landscape oriented
    pdf = SimpleDocTemplate(stream, pagesize=landscape(letter))

    # Table is in a frame
    table = Table(self.lines, [1.5* inch ] * 7, self.row_heights, style=self.tableStyle, repeatRows=1)
    table.wrap(0,0) # important hacky way to span on full width
    tableFrame = Frame(inch / 2, inch / 2, 10*inch, 7*inch)

    # RunReport logo
    logo = Image(os.path.join(settings.ROOT, 'front/img/logo_ligne.png'))
    logo.drawHeight = 2.2*inch*logo.drawHeight / logo.drawWidth
    logo.drawWidth = 2.2*inch

    # Plan infos are in a frame, in top left corner
    context = {
      'site' : self.site,
      'plan' : self.plan,
    }
    title = Paragraph(render_to_string('plan/export.pdf.title.html', context), self.titleStyle)

    # Add table elements
    pdf.addPageTemplates([
      PageTemplate(id='table', frames=[tableFrame]),
    ])
    story = [
      logo,
      title,
      Spacer(1, 0.4*inch), # make room for header
      table, # the plan
    ]
    pdf.build(story)

    if isinstance(stream, StringIO):
      output = stream.getvalue()
      stream.close()
      return output

    return None
