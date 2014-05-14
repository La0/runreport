from django.core.management.base import BaseCommand, CommandError
from sport.models import SportDay, SportSession, Sport

class Command(BaseCommand):
  def handle(self, *args, **options):
    days = SportDay.objects.all().exclude(type='rest').order_by('date')
    sport = Sport.objects.get(slug='running')
    for i, day in enumerate(days):
      print '%d/%d %s %s' % (i, days.count(), day.date, day.week.user.username)

      # Already created with Garmin activities
      running_sessions = day.sessions.filter(sport=sport)
      if running_sessions.count() > 1:
        # no creations or modifications
        print ' > Too many sessions already'
        continue

      elif running_sessions.count() == 1:
        # Keep user input time & distance
        s = running_sessions[0]
        if s.time != day.time or s.distance != day.distance:
          s.time = day.time
          s.distance = day.distance
          s.save()
          print ' > Update existing running SportSession'
        else:
          print ' > Keep existing running SportSession'
      else:
        # Init session with running
        SportSession.objects.create(day=day, sport=sport, time=day.time, distance=day.distance)
        print ' > Create running SportSession'
