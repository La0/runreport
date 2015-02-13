from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

class Place(models.Model):
  '''
  A place to meet athletes and do some sport
  '''
  name = models.CharField(_('Name'), max_length=255)
  creator = models.ForeignKey('users.Athlete', related_name='places')
  club = models.ForeignKey('club.Club', null=True, blank=True, related_name='places')

  # Address
  address = models.CharField(_('Address'), max_length=255)
  zipcode = models.CharField(_('Zip Code'), max_length=10)
  city = models.CharField(_('City'), max_length=255)
  point = models.PointField(null=True, blank=True)

  objects = models.GeoManager()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
