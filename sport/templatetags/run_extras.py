from django import template
from datetime import time, timedelta

register = template.Library()

@register.filter(is_safe=True)
def total_time(t):
  '''
  Display total time as a nicely formatted string
  from a timestamp or timedelta
  '''
  if isinstance(t, timedelta):
    t = t.total_seconds()

  out = ''
  if t is None:
    return '-'
  try:
    t = int(t)
  except:
    return '-'

  hours = int(t / 3600)
  minutes = int((t % 3600) / 60)

  return '%dh%02d' % (hours, minutes)
