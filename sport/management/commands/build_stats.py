from django.core.management.base import BaseCommand, CommandError
from sport.models import SportDay
from sport.stats import StatsMonth
from users.models import Athlete
from datetime import date, timedelta

class Command(BaseCommand):

  def handle(self, *args, **options):
    today = date.today()
    print today

    users = Athlete.objects.all()

    for user in users:
      print user

      # Search first active day
      first = SportDay.objects.filter(week__user=user).order_by('date').first()
      if not first:
        print ' !! No day, no stats !!'
        continue

      # Buil StatsMonth until now
      for year in range(first.date.year, today.year+1):
        for month in range(1, 13):

          # Skip unecessary months (no data)
          if (year, month) < (first.date.year, first.date.month) or (year, month) > (today.year, today.month):
            continue
        
          # Build StatsMonth
          stats = StatsMonth(user, year, month)
          stats.build()
          print ' >> %d / %d' % (year, month)
