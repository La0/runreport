from celery.result import AsyncResult
from datetime import datetime, timedelta
import math
from PIL import Image

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

def seconds_humanize(t, short=False):
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

  if short and not hours:
    return '%02d:%02d' % (minutes, seconds)
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


def crop_image(source, destination, size=400, image_format='JPEG'):
  '''
  Crop an image using pillow
  '''
  # Load image
  img = Image.open(source)
  w,h = img.size
  small_size = min(w,h)

  # Resize before crop ?
  if small_size > size:
    ratio = float(size) / float(small_size)
    w = int(math.floor(w * ratio))
    h = int(math.floor(h * ratio))
    img = img.resize((w, h))
  else:
    # Use smallest side as crop
    size = small_size

  crop_box = None
  if w < h:
    # Vertical Crop
    offset = int(math.floor((h - size) / 2))
    crop_box = (0, offset, w, h - offset)
  elif w > h:
    # Horizontal crop
    offset = int(math.floor((w - size) / 2))
    crop_box = (offset, 0, w - offset, h)

  # Do the crop
  if crop_box:
    img = img.crop(crop_box)

  # Save the resulting image
  img.save(destination, image_format)
