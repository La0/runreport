from django import template
from datetime import time, timedelta
from helpers import seconds_humanize

register = template.Library()

@register.filter(is_safe=True)
def total_time(t):
  '''
  Display total time as a nicely formatted string
  from a timestamp or timedelta
  '''
  if isinstance(t, timedelta):
    t = t.total_seconds()

  return seconds_humanize(t)
