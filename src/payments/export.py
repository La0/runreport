from django.utils.translation import ugettext_lazy as _
from reportlab.platypus import Table, Paragraph, Image, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib.enums import TA_CENTER
from reportlab.rl_config import defaultPageSize
from django.utils import translation
from django.conf import settings
from StringIO import StringIO


class PeriodPdfExporter(object):
    '''
    Export a period as pdf
    for a given pdf
    '''
    period = None

    # Styles
    tableStyle = []
    dateStyle = None
    sessionStyle = None
    titleStyle = None

    # Pages size
    width = 0
    height = 0

    def __init__(self, period):
        self.period = period
        self.setup_styles()
        self.width = defaultPageSize[0]
        self.height = defaultPageSize[1]

        # Check language is activated
        if translation.get_language() is None:
            translation.activate(settings.LANGUAGE_CODE)

    def setup_styles(self):
        # Build style sheets
        s1, s2, s3 = getSampleStyleSheet(), getSampleStyleSheet(), getSampleStyleSheet()
        self.sessionStyle, self.dateStyle = s1['Normal'], s2['Normal']
        self.titleStyle = s3['Heading2']
        self.titleStyle.alignment = TA_CENTER
        self.periodStyle = s3['Heading2']
        self.periodStyle.alignment = TA_CENTER
        self.periodStyle.textColor = colors.grey

        # Base table style
        self.tableStyle = [
            # Grid around the table
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]

    def build_table(self):
        '''
        Build the bill table
        '''
        data = [[
            _('Period'),
            _('Athletes'),
            _('Trainers'),
            _('Total'),
        ], ]

        # Add roles calc
        titles = {
            'premium_s': _('Period of 1 month as Premium Small'),
            'premium_m': _('Period of 1 month as Premium Medium'),
            'premium_l': _('Period of 1 month as Premium Large'),
        }
        data.append([
            titles.get(self.period.level),
            str(self.period.nb_athletes),
            str(self.period.nb_trainers),
            str(self.period.amount),
        ])

        t = Table(data)
        t.setStyle(self.tableStyle)

        return t

    def render(self, stream=None):
        '''
        Render the pdf with current lines & style
        '''
        # Use a buffer when no stream is given
        if stream is None:
            stream = StringIO()

        # Canvas is portrait oriented
        pdf = SimpleDocTemplate(stream, pagesize=portrait(letter))

        # RunReport logo
        logo = Image('../front/img/logo_ligne.png')
        logo.drawHeight = 2.2 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2.2 * inch

        title_str = _('Payment for club %s') % self.period.club.name
        title = Paragraph(title_str, self.titleStyle)
        date_fmt = '%d/%m/%Y'
        period_str = _('From %s to %s') % (self.period.start.strftime(
            date_fmt), self.period.end.strftime(date_fmt))
        period = Paragraph(period_str, self.periodStyle)

        # Add table elements
        story = [
            logo,
            title,
            period,
            Spacer(1, 0.4 * inch),  # make room for header
            self.build_table(),  # the period
        ]
        pdf.build(story)

        if isinstance(stream, StringIO):
            output = stream.getvalue()
            stream.close()
            return output

        return None
