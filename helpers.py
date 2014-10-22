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

def gpolyline_decode(point_str):
  '''
  From : https://gist.github.com/signed0/2031157
  Doc : https://developers.google.com/maps/documentation/utilities/polylinealgorithm
  Decodes a polyline that has been encoded using Google's algorithm
  http://code.google.com/apis/maps/documentation/polylinealgorithm.html
  This is a generic method that returns a list of (latitude, longitude)
  tuples.
  :param point_str: Encoded polyline string.
  :type point_str: string
  :returns: List of 2-tuples where each tuple is (latitude, longitude)
  :rtype: list
  '''

  # sone coordinate offset is represented by 4 to 5 binary chunks
  coord_chunks = [[]]
  for char in point_str:

    # convert each character to decimal from ascii
    value = ord(char) - 63

    # values that have a chunk following have an extra 1 on the left
    split_after = not (value & 0x20)
    value &= 0x1F

    coord_chunks[-1].append(value)

    if split_after:
        coord_chunks.append([])

  del coord_chunks[-1]

  coords = []

  for coord_chunk in coord_chunks:
    coord = 0

    for i, chunk in enumerate(coord_chunk):
      coord |= chunk << (i * 5)

    #there is a 1 on the right if the coord is negative
    if coord & 0x1:
      coord = ~coord #invert
    coord >>= 1
    coord /= 100000.0

    coords.append(coord)

  # convert the 1 dimensional list to a 2 dimensional list and offsets to
  # actual values
  points = []
  lat = 0
  lng = 0
  for i in xrange(0, len(coords) - 1, 2):
    if coords[i] == 0 and coords[i + 1] == 0:
      continue

    lat += coords[i]
    lng += coords[i + 1]
    # a round to 6 digits ensures that the floats are the same as when
    # they were encoded
    points.append((round(lat, 6), round(lng, 6)))

  return points
