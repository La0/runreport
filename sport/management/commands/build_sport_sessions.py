from django.core.management.base import BaseCommand, CommandError
from sport.models import SportDay, SportSession, Sport

class Command(BaseCommand):
  def handle(self, *args, **options):
    days = SportDay.objects.all().order_by('date')
    sport = Sport.objects.get(slug='running')
    fields = (
      'name',
      'comment',
      'time',
      'distance',
      'type',
      'race_category',
    )
    for i, day in enumerate(days):
      print '%d/%d %s %s' % (i, days.count(), day.date, day.week.user.username)

      # Keep user input
      if day.sessions.count() >= 1:
        s = day.sessions.all()[0]
        modified = False
        for field in fields:
          user_val = getattr(day, field)
          if getattr(s, field) != user_val:
            setattr(s, field, user_val)
            modified = True
        if modified:
          s.save()
        print ' > Update existing running SportSession'
      else:
        # Init session with running
        SportSession.objects.create(day=day, sport=sport, time=day.time, distance=day.distance, name=day.name, comment=day.comment, type=day.type, race_category=day.race_category)
        print ' > Create running SportSession'
