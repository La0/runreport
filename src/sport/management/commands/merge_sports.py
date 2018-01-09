# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from sport.models import Sport, SportSession

class Command(BaseCommand):
  # Sports
  source = None
  dest = None

  # Sport sessions
  sessions = None

  def handle(self, source_slug, dest_slug, *args, **kwargs):
    try:
      self.source = Sport.objects.get(slug=source_slug)
      self.dest = Sport.objects.get(slug=dest_slug)
    except Exception, e:
      raise CommandError('Invalid sport: %s' % str(e))

    print('From #%d %s to #%d %s' % (self.source.pk, self.source.name, self.dest.pk, self.dest.name))

    # Load sessions
    self.sessions = SportSession.objects.filter(sport=self.source).order_by('day__date')

    self.merge_tracks()
    self.adopt_sport()

  def merge_tracks(self):
    '''
    Merge tracks from sessions with source Sport
    '''
    for s in self.sessions.filter(track__isnull=False):
      track = s.track
      print(s.day.week.user, s.id, s.name, track.id)

      # Available sessions
      targets = s.day.sessions.exclude(pk=s.pk).filter(sport=self.dest, track__isnull=True)
      nb = targets.count()
      target = None
      if nb > 1:
        # User must pick a target
        while not target:
          for t in targets:
            print(' > %d %s - %s km - %s' % (t.pk, t.name, t.distance, t.time))
          try:
            pk = input('pk ? ')
            target = targets.get(pk=int(pk))
          except:
            continue

      elif nb == 1:
        # Pick only one
        target = targets.first()

      # Set track on target
      if target:
        track.session = target
        track.save()

        # Update the target sport
        target.sport = self.dest
        target.save()

        # Cleanup session ?
        if not s.comment or s.comment == '':
          s.delete()

      else:
        # At least update the sport
        s.sport = self.dest
        s.save()


  def adopt_sport(self):
    '''
    Source adopts dest
    '''
    self.source.parent = self.dest
    self.source.depth = 2
    self.source.save()

