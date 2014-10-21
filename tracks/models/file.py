from django.db import models
import os
from django.conf import settings
import hashlib

class TrackFile(models.Model):
  track = models.ForeignKey('tracks.Track', related_name='files')
  name = models.CharField(max_length=50, db_index=True, default='details')
  md5 = models.CharField(max_length=32)

  class Meta:
    unique_together = (
      ('track', 'name'),
    )

  def get_data_path(self):
    return os.path.join(settings.TRACK_DATA, self.track.provider, '%s_%s.json' % (self.track.id, self.name))

  def set_data(self, data):
    # Check dir
    path = self.get_data_path()
    path_dir = os.path.dirname(path)
    if not os.path.isdir(path_dir):
      os.makedirs(path_dir)

    # Dump in file
    fd = open(path, 'w+')
    fd.write(data)
    fd.close()

  def get_data(self, name):
    path = self.get_data_path(name)
    if not os.path.exists(path):
      return None

    # Check md5 before giving data
    if self.md5 is None:
      return None
    fd = open(self.get_data_path(name), 'r')
    data = fd.read()
    h = hashlib.md5(data).hexdigest()
    fd.close()
    if h != self.md5:
      raise Exception("Invalid data file %s" % path)
    return data

