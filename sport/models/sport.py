# coding=utf-8
from django.db import models
from . import SESSION_TYPES

class Sport(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True)
  parent = models.ForeignKey('Sport', null=True)
  depth = models.IntegerField(default=0)

  class Meta:
    db_table = 'sport_list'
    app_label = 'sport'

  def __unicode__(self):
    return self.name

  def get_parent(self):
    # Always give a valid parent
    if self.depth <= 1 or not self.parent:
      return self
    return self.parent

  def get_category(self):
    # Always give a valid parent category
    return self.get_parent().slug

class SportSession(models.Model):
  day = models.ForeignKey('SportDay', related_name="sessions")
  sport = models.ForeignKey(Sport)
  time = models.TimeField(null=True, blank=True)
  distance = models.FloatField(null=True, blank=True)
  name = models.CharField(max_length=255, null=True, blank=True)
  comment = models.TextField(null=True, blank=True)
  type = models.CharField(max_length=12, default='training', choices=SESSION_TYPES)
  race_category = models.ForeignKey('RaceCategory', null=True, blank=True)

  class Meta:
    db_table = 'sport_session'
    app_label = 'sport'

  def save(self, *args, **kwargs):
    # No race category when we are not in race
    if self.type != 'race':
      self.race_category = None

    # Only allow depth 1 sports
    if self.sport.depth != 1:
      raise Exception("Invalid sport '%s', only level 1 authorized for SportSession" % self.sport)

    super(SportSession, self).save(*args, **kwargs)

  def has_garmin(self):
    # Helper for templates (no hasattr)
    return hasattr(self, 'garmin_activity')
