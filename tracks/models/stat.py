from django.db import models
from datetime import datetime
from helpers import seconds_humanize

class TrackStat(models.Model):
  track = models.ForeignKey('tracks.Track', related_name='stats')
  name = models.CharField(max_length=50)
  value = models.FloatField()
  unit = models.CharField(max_length=50)

  class Meta:
    unique_together = (('track', 'name'), )

  def display(self):
    '''
    Format nicely every stat
    '''

    # Detect infinity !
    if self.value == float('-Inf'):
      return "-&infin;"
    if self.value == float('Inf'):
      return "&infin;"

    # Distances
    if self.unit in ('kilometer', 'km'):
      return '%s km' % round(self.value, 2)
    if self.unit in ('meter', 'm'):
      return '%s m' % round(self.value, 1)

    # Speed
    if self.unit in ('min/km', ):
      return '%s min/km' % seconds_humanize(self.value * 60, short=True)
    if self.unit in ('m/s', ):
      return '%s min/km' % seconds_humanize(1000 / self.value, short=True)

    # Time
    if self.name[0:4] == 'time':
      value = self.unit == 'ms' and self.value / 1000.0 or self.value
      dt = datetime.fromtimestamp(value)
      return dt
    if self.unit in ('second', 's'):
      return seconds_humanize(self.value)

    # Energy
    if self.unit in ('kilocalorie', ):
      return '%s kcal' % round(self.value, 0)

    # Default
    return '%f %s' % (self.value, self.unit)
