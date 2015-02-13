import requests
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import Point

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


  def geocode(self):
    '''
    Use OSM Geocoding to fetch GPS position
    '''
    url = 'http://nominatim.openstreetmap.org/search/'
    params = {
      'format' : 'json',
      'q' : '%s %s %s' % (self.address, self.zipcode, self.city),
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
      raise Exception('Invalid OSM response')

    results = res.json()
    if not results:
      raise Exception('No geocoding results')

    # Use first result
    result = results[0]

    self.point = Point(float(result['lat']), float(result['lon']))

    return self.point
