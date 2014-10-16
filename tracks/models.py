from django.contrib.gis.db import models
from sport.models import SportSession


class Track(models.Model):
  session = models.OneToOneField(SportSession, related_name='track')

  # PolyLines
  raw = models.LineStringField()
  objects = models.GeoManager()


  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)


