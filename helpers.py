from datetime import datetime

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

def date_to_day(date, day=1):
  '''
  From any date, get a date in the same week
  Default to monday
  '''
  week = int(date.strftime('%W'))
  return datetime.strptime('%d %d %d' % (date.year, week, day), '%Y %W %w').date()

def date_to_week(date):
  '''
  From any date, export the week and year tuple
  '''
  return int(date.strftime('%W')), date.year

def week_to_date(year, week, day=1):
  '''
  From any year+week to a given day in its week
  Default to monday
  '''
  return datetime.strptime('%d %d %d' % (year, week, day), '%Y %W %w').date()
