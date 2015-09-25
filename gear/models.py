from django.db import models
import vinaigrette


class GearCategory(models.Model):
  '''
  Categories of gear
  Moderated, but editable by users
  '''
  name = models.CharField(max_length=250)
  official = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return self.name

# i18n
vinaigrette.register(GearCategory, ['name', ])


class GearBrand(models.Model):
  '''
  Consumer brand of gear
  Moderated, but editable by users
  '''
  name = models.CharField(max_length=250)
  official = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return self.name


class GearItem(models.Model):
  '''
  Gear piece from a user
   * default sports
   * linked to sessions
  '''
  # Base
  name = models.CharField(max_length=250)
  description = models.TextField()

  # Links
  category = models.ForeignKey(GearCategory, related_name='items')
  brand = models.ForeignKey(GearBrand, related_name='items')
  user = models.ForeignKey('users.Athlete', related_name='items')
  sports = models.ManyToManyField('sport.Sport', blank=True)
  sessions = models.ManyToManyField('sport.SportSession', blank=True)

  # Dates
  start = models.DateTimeField(null=True, blank=True)
  end = models.DateTimeField(null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return self.name

