from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, Frame, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_CENTER
from reportlab.rl_config import defaultPageSize
from coffin.template.loader import render_to_string
from django.contrib.sites.models import get_current_site
from django.utils import formats
from helpers import week_to_date

class PlanPdfExporter(object):
  '''
  Export a plan as pdf
  '''
  plan = None
  site = None
  lines = None

  # Styles
  tableStyle = [
    # Grid around the table
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
  ]
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

  def setup_styles(self):
    # Build style sheets
    s1, s2, s3 = getSampleStyleSheet(), getSampleStyleSheet(), getSampleStyleSheet()
    self.sessionStyle, self.dateStyle = s1['Normal'], s2['Normal']
    self.titleStyle = s3['Heading2']
    self.dateStyle.backColor = colors.grey
    self.dateStyle.textColor = colors.white
    self.dateStyle.alignment = TA_CENTER

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
    for week_pos in range(0, self.plan.get_weeks_nb()):
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
        for session in self.plan.sessions.filter(week=week_pos, day=day_pos):
          context = {
            'session' : session,
          }
          sessions.append(Paragraph(render_to_string('plan/export.pdf.session.html', context), self.sessionStyle))

        week.append(sessions or '')
      if dates:
        self.lines.append(dates)
      self.lines.append(week)


  def render(self, stream):
    '''
    Render the pdf with current lines & style
    '''
    # Build lines
    self.add_days()
    self.build_lines()

    # Canvas is landscape oriented
    pdf = canvas.Canvas(stream, pagesize=landscape(letter))

    # Table is in a frame
    table = Table(self.lines, style=self.tableStyle)
    tableFrame = Frame(inch / 2, inch / 2, 10*inch, 7*inch)
    tableFrame.addFromList([ table, ], pdf)

    # Plan infos are in a frame, in top left corner
    infoFrame = Frame(inch / 2, 7.5 * inch, 7*inch, 0.6 * inch)
    context = {
      'site' : self.site,
      'plan' : self.plan,
    }
    title = Paragraph(render_to_string('plan/export.pdf.title.html', context), self.titleStyle)
    infoFrame.addFromList([ title, ], pdf)

    # Logo is in a frame in top right corner
    logoPos = (inch*7.5, 7.6 * inch, 3*inch, 0.6 * inch)
    logoFrame = Frame(*logoPos)
    logo = Image('./medias/img/logo_ligne.png')
    logo.drawHeight = 2.2*inch*logo.drawHeight / logo.drawWidth
    logo.drawWidth = 2.2*inch
    logoFrame.addFromList([ logo, ], pdf)

    # Logo is clickable
    pdf.linkURL('http://%s' % self.site.domain, (logoPos[0], logoPos[1], logoPos[0]+logoPos[2], logoPos[1]+logoPos[3]))

    # Cleanly close pdf
    pdf.showPage()
    pdf.save()
