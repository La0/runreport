# coding=utf-8
from django.db import models

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

  def get_category(self):
    # Always give a valid parent category
    if self.depth <= 1 or not self.parent:
      return self.slug
    return self.parent.get_category()

