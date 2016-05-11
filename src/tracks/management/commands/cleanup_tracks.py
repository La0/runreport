from django.core.management.base import BaseCommand, CommandError
from tracks.models import Track
from django.db.models import Count


class Command(BaseCommand):

  def handle(self, *args, **kwargs):

    # Cleanup doublons
    doubles = Track.objects.values('session_id').annotate(nb=Count('session_id')).filter(nb__gt=1)
    if not doubles:
      raise CommandError('No doubles found !')

    for d in doubles:
      print d['session_id']

      Track.objects.filter(session_id=d['session_id']).last().delete()
