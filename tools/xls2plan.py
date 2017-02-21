import os
import xlrd
import re
import json
from datetime import date, timedelta
import logging
import sys
logger = logging.getLogger(__name__)

DAYS = [u'lundi', u'mardi', u'mercredi', u'jeudi', u'vendredi', u'samedi', u'dimanche']
WEEK_NB_RE = re.compile(r'^Semaine (\d+)')
WEEK_DATE_RE = re.compile(r'(\d{2})\.(\d{2})\.(\d{4})')


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)


class Xls2Plan(object):

    def __init__(self, path):
        assert os.path.exists(path)
        self.book = xlrd.open_workbook(path, logfile=sys.stderr)

    def run(self):

        # Just use first sheet.
        self.sheet = self.book.sheets()[0]

        # Find days positions
        days_row, days_cols = self.find_days()
        logger.info('Days are on row {}'.format(days_row))

        # Find weeks, just after days
        weeks = self.find_weeks(days_row + 1)
        logger.info('Weeks nb = {}'.format(len(weeks)))

        # Fill all weeks
        for week in weeks:
            week['days'] = self.parse_week(week, days_cols)

        # Dump as json on stdout
        plan = {
            'name': self.sheet.name,
            'trainer': self.book.user_name,
            'weeks': weeks,
        }
        out = json.dumps(plan, indent=4, sort_keys=True, cls=DateEncoder)
        print(out)

        logger.info('Done.')

    def find_days(self):
        """
        Find days row and their positions (offset)
        """

        for row in range(self.sheet.nrows):
            cols = [
                i
                for i,v in enumerate(self.sheet.row_values(row))
                if v.lower() in DAYS
            ]
            if cols and len(cols) == 7:
                return row, cols

        raise Exception('No week days found in sheet')

    def find_weeks(self, start):
        """
        Find weeks in first cols
        """
        weeks = []
        for row in range(start, self.sheet.nrows):
            row_value = self.sheet.cell_value(row, 0)
            week_nb = WEEK_NB_RE.search(row_value)
            week_date = WEEK_DATE_RE.search(row_value)
            if week_nb:
                # Create new week
                weeks.append({
                    'nb' : int(week_nb.group(1)),
                    'rows' : [],
                })

            elif week_date:
                # Append date to last week
                end = date(*map(int, week_date.groups()[::-1]))
                start = end - timedelta(days=6)
                weeks[-1].update({
                    'start' : start,
                    'end' : end,
                })

            # Always add row to last week
            if weeks:
                weeks[-1]['rows'].append(row)

        if not weeks:
            raise Exception('No weeks found')

        return weeks

    def parse_week(self, week, days_cols):
        """
        Parse a week content
        day by day
        """
        logger.info('Parsing week {nb} from {start} to {end}'.format(**week))
        assert isinstance(week.get('start'), date)

        out = []
        for day, col in enumerate(days_cols):
            day_content = []
            for row in week['rows']:
                cell = self.sheet.cell(row, col)
                if cell.ctype == xlrd.XL_CELL_EMPTY:
                    continue

                # Build text content as array
                day_content += filter(None, cell.value.split('\n'))

            # Store day content in out structure
            if day_content:
                out.append({
                    'day' : week['start'] + timedelta(days=day),
                    'title' : ' - '.join(day_content[0:2]),
                    'content' : '\n'.join(day_content),
                })

        return out


if __name__ == '__main__':
    x = Xls2Plan(sys.argv[1])
    x.run()
