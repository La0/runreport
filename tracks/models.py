from django.contrib.gis.db import models
from sport.models import SportSession


class Track(models.Model):
  session = models.OneToOneField(SportSession, related_name='track')

  # PolyLines
  raw = models.LineStringField()
  simple = models.LineStringField(null=True, blank=True)
  objects = models.GeoManager()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def simplify(self, tolerance=0.0001):
    '''
    Simplify the raw polyline
    '''
    self.simple = self.raw.simplify(tolerance)
    return self.simple

