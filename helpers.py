from celery.result import AsyncResult
from datetime import datetime, timedelta

def nameize(s, max = 40):
  import re, unicodedata

  # Remove all accents
  try:
    s = unicode(s, 'ISO-8859-1')
  except:
    pass
  s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')

  # Remove all non allowed chars
  s = re.sub('[^a-z0-9 ]', '', s.strip().lower(),)

  # Remove multiple spaces
  s = re.sub('[ ]+', ' ', s.strip().lower(),)

  # Limit words to match chars length
  words = s.split(' ')
  cpt = 0
  nb = 0
  for w in words:
    cpt += len(w)
    if cpt > max:
      break
    nb += 1
  s = '_'.join(words[0:nb])

  return s

def date_to_day(date, day=0):
  '''
  From any date, get a date in the same week
  Default to monday
  '''
  offset = date.weekday() - day
  date -= timedelta(days=offset)
  return date

def date_to_week(date):
  '''
  From any date, export the week and year tuple,
  but always use the monday
  '''
  date = date_to_day(date, day=0)
  return int(date.strftime('%W')), date.year

def week_to_date(year, week, day=1):
  '''
  From any year+week to a given day in its week
  Default to monday
  '''
  return datetime.strptime('%d %d %d' % (year, week, day), '%Y %W %w').date()


def check_task(model):
  '''
  Check the attached task is still running
   if not, clean te reference
  '''
  if not model.task:
    return False

  # Check task
  result = AsyncResult(model.task)
  if result.state in ('SUCCESS', 'FAILURE'):
    model.task = None
    model.save()

  return result.state

def time_to_seconds(t):
  return t.hour*3600 + t.minute*60 + t.second

def seconds_humanize(t):
  '''
  Format total seconds as HH:MM:SS
  Never display days (1 day 1h = 25h)
  '''
  out = ''
  if t is None:
    return '-'
  try:
    t = int(t)
  except:
    return '-'

  hours = int(t / 3600)
  minutes = int((t % 3600) / 60)
  seconds = t % 60

  return '%d:%02d:%02d' % (hours, minutes, seconds)
