from django.core.management.base import BaseCommand
from badges.models import Badge

class Command(BaseCommand):

  def handle(self, *args, **options):

    for b in Badge.objects.all():
      try:
        if b.image != 'badges/default.png':
          raise Exception('Already built %s' % b.image)
        b.build_image()
        print('Built %s' % b.image.path)
      except Exception as e:
        print(e.message)
