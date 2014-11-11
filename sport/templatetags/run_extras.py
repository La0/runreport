from django import template
from datetime import time, timedelta
from helpers import seconds_humanize

register = template.Library()

@register.filter(is_safe=True)
def total_time(t, short=False):
  '''
  Display total time as a nicely formatted string
  from a timestamp or timedelta
  '''
  if isinstance(t, timedelta):
    t = t.total_seconds()

  return seconds_humanize(t, short)

@register.filter(is_safe=True)
def convert_speed(s):
  '''
  Convert a speed in m/s
  to a nicer time display in min/km
  '''
  return s > 0 and seconds_humanize(1000.0 / s, True) or 0

@register.filter(is_safe=True)
def convert_speed_kmh(s):
  '''
  Convert a speed in m/s
  to a nicer time display in km/h
  '''
  return s > 0 and s*3.6 or 0

@register.filter(is_safe=True)
def total_distance(d):
  '''
  Simply display kilometers when > 1000m
  default to meters
  '''
  if d >= 1000:
    return '%s km' % round(d / 1000.0, 1)
  return '%d m' % d
