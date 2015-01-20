from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from tracks.models import Track
import os
import shutil

class Command(BaseCommand):

  def handle(self, *args, **kwargs):

    # Check error dir
    error_dir = settings.TRACK_DATA + '_errors'


    # Cleanup providers
    for f in self.listdir(settings.TRACK_DATA):

      # Get track id
      name = os.path.basename(f)
      if '_' not in name:
        raise Exception('Invalid file %s' % f)
      pk = int(name[:name.index('_')])

      # Fetch track
      try:
        Track.objects.get(pk=pk)
      except:
        print 'err : %s' % f

        # Move in error dir
        dest = os.path.join(error_dir, f.replace(settings.TRACK_DATA + '/', ''))
        dest_dir = os.path.dirname(dest)
        if not os.path.isdir(dest_dir):
          os.makedirs(dest_dir)
        shutil.move(f, dest)

  def listdir(self, path):
    '''
    Traverse recursively a dir, using generators
    '''
    for f in os.listdir(path):
      full = os.path.join(path, f)
      if os.path.isdir(full):
        for sub in self.listdir(full):
          yield sub
      else:
        yield full

