# coding=utf-8
from django.db import models
#from .organisation import SportDay

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

  class Meta:
    db_table = 'sport_session'
    app_label = 'sport'
    unique_together = (('day', 'sport'), )

  def save(self, *args, **kwargs):
    # Only allow depth 1 sports
    if self.sport.depth != 1:
      raise Exception("Invalid sport '%s', only level 1 authorized for SportSession" % self.sport)

    super(SportSession, self).save(*args, **kwargs)
