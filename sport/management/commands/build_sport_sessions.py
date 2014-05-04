from django.core.management.base import BaseCommand, CommandError
from sport.models import SportDay, SportSession, Sport

class Command(BaseCommand):
  def handle(self, *args, **options):
    days = SportDay.objects.all().exclude(type='rest').order_by('date')
    sport = Sport.objects.get(slug='running')
    for i, day in enumerate(days):
      print '%d/%d %s %s' % (i, days.count(), day.date, day.week.user.username)

      # Init session with running
      session, _ = SportSession.objects.get_or_create(day=day, sport=sport)
      session.time = day.time
      session.distance = day.distance
      session.save()
