from django.db import models
import os
from django.conf import settings
import hashlib
import json

class TrackFile(models.Model):
  track = models.ForeignKey('tracks.Track', related_name='files')
  name = models.CharField(max_length=50, db_index=True, default='details')
  md5 = models.CharField(max_length=32)

  class Meta:
    unique_together = (
      ('track', 'name'),
    )

  def get_data_path(self):
    dt = self.track.session.day.date
    parts = [
      settings.TRACK_DATA,
      self.track.provider,
      str(dt.year),
      str(dt.month),
      str(dt.day),
      '%s_%s.json' % (self.track.id, self.name),
    ]
    return os.path.join(*parts)

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

  def get_data(self, format_json=True):
    path = self.get_data_path()
    if not os.path.exists(path):
      return None

    # Check md5 before giving data
    if self.md5 is None:
      return None

    with open(path, 'r') as fd:
      data = fd.read()

    h = hashlib.md5(data).hexdigest()
    if h != self.md5:
      raise Exception("Invalid data file %s" % path)

    if format_json:
      return json.loads(data)

    return data

