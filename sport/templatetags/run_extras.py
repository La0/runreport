from django import template
from datetime import time

register = template.Library()

@register.filter(is_safe=True)
def days_time(t, day_name='day', time_format='%H:%M:%S'):
  '''
  Display nb of days and nicely formatted time
  from a timestamp
  '''
  out = ''
  if t is None:
    return '-'
  try:
    t = int(t)
  except:
    return '-'
  days = int(t / 86400)
  if days > 0:
    out += '%d %s%s ' % (days, day_name, days > 1 and 's' or '')
  t = t % 86400
  t = time(t / 3600, (t % 3600) / 60, t % 60)
  out += t.strftime(time_format)

  return out

