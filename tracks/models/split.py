from django.contrib.gis.db import models

class TrackSplit(models.Model):
  track = models.ForeignKey('tracks.Track', related_name='splits')
  position = models.IntegerField()

  distance = models.FloatField(default=0) # in m
  time = models.FloatField(default=0) # in seconds
  speed = models.FloatField(default=0) # in m/s
  speed_max = models.FloatField(default=0) # in m/s
  elevation_min = models.FloatField(default=0) # in m
  elevation_max = models.FloatField(default=0) # in m
  elevation_gain = models.FloatField(default=0) # in m
  elevation_loss = models.FloatField(default=0) # in m
  energy = models.FloatField(default=0) # in kcal

  # Totals are values since the beginning
  distance_total = models.FloatField(default=0)
  time_total = models.FloatField(default=0)

  # Dates
  date_start = models.DateTimeField(null=True, blank=True)
  date_end = models.DateTimeField(null=True, blank=True)

  # Geo positions
  position_start = models.PointField(null=True, blank=True)
  position_end = models.PointField(null=True, blank=True)
  objects = models.GeoManager()

  class Meta:
    unique_together = (('track', 'position'), )
