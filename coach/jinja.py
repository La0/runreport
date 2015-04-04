# coding=utf-8
from jinja2 import Environment, Template
from importlib import import_module
from django.conf import settings
from coach.menu import add_pages
from datetime import timedelta
from helpers import seconds_humanize

def environment(**options):
  '''
  Setup Jinja2 environment:
  '''
  # TODO: In prod use cached templates
  if not settings.DEBUG:
     options['loader'] = 'django.template.loaders.cached.Loader'

  # Init environment
  env = Environment(**options)

  # Use template with some common context
  env.template_class = ContextTemplate

  # Add our custom filters
  env.filters.update({
    'addcss' : addcss,
    'total_time' : total_time,
    'convert_speed' : convert_speed,
    'convert_speed_kmh' : convert_speed_kmh,
    'total_distance' : total_distance,
  })

  # Add constants from settings
  keys = ['DEBUG', 'PIWIK_HOST', 'PIWIK_ID', 'FACEBOOK_ID', ]
  env.globals.update(dict([(k, getattr(settings, k, None)) for k in keys]))

  # Setup translations
  translation = import_module('django.utils.translation')
  env.install_gettext_translations(translation, newstyle=False)

  return env


class ContextTemplate(Template):
  '''
  Replace context processors
  Every data from request is processed here
  '''
  def render(self, context, *args, **kwargs):
    request = context['request']

    # Add user in context
    context['user'] = request.user

    # Add menu
    context.update(add_pages(request))

    return super(ContextTemplate, self).render(context, *args, **kwargs)


# Template filters
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

def total_time(t, short=False):
  '''
  Display total time as a nicely formatted string
  from a timestamp or timedelta
  '''
  if isinstance(t, timedelta):
    t = t.total_seconds()

  return seconds_humanize(t, short)

def convert_speed(s):
  '''
  Convert a speed in m/s
  to a nicer time display in min/km
  '''
  return s > 0 and seconds_humanize(1000.0 / s, True) or 0

def convert_speed_kmh(s):
  '''
  Convert a speed in m/s
  to a nicer time display in km/h
  '''
  return s > 0 and s*3.6 or 0

def total_distance(d):
  '''
  Simply display kilometers when > 1000m
  default to meters
  '''
  if d >= 1000:
    return '%s km' % round(d / 1000.0, 1)
  return '%d m' % d
