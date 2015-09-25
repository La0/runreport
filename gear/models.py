from django.db import models
from django.utils.translation import ugettext_lazy as _
import vinaigrette

class GearModerated(models.Model):
  '''
  Common class between Category & Brand
  '''
  name = models.CharField(max_length=250)
  owner = models.ForeignKey('users.Athlete')
  official = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True

  def __unicode__(self):
    return self.name

class GearCategory(GearModerated):
  '''
  Categories of gear
  Moderated, but editable by users
  '''

# i18n
vinaigrette.register(GearCategory, ['name', ])


class GearBrand(GearModerated):
  '''
  Consumer brand of gear
  Moderated, but editable by users
  '''


class GearItem(models.Model):
  '''
  Gear piece from a user
   * default sports
   * linked to sessions
  '''
  # Base
  name = models.CharField(max_length=250, verbose_name=_('Equipment name'))
  description = models.TextField(_('Description'))

  # Links
  category = models.ForeignKey(GearCategory, related_name='items', verbose_name=_('Category'))
  brand = models.ForeignKey(GearBrand, related_name='items', verbose_name=_('Brand'))
  user = models.ForeignKey('users.Athlete', related_name='items')
  sports = models.ManyToManyField('sport.Sport', blank=True, verbose_name=_('Default sports'))
  sessions = models.ManyToManyField('sport.SportSession', blank=True)

  # Date
  start = models.DateTimeField(null=True, blank=True, verbose_name=_('Start usage date'))
  end = models.DateTimeField(null=True, blank=True, verbose_name=_('End usage date'))
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ('user', 'category', 'brand', 'created')

  def __unicode__(self):
    return self.name

