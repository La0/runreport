from django.core.management.base import BaseCommand
from sport.models import SportDay
from sport.stats import StatsMonth, StatsWeek
from users.models import Athlete
from datetime import date
from optparse import make_option
import calendar

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--username',
      action='store',
      dest='username',
      type='string',
      default=False,
      help='Ran the import on the specified user.'),
  )

  def handle(self, *args, **options):
    today = date.today()

    users = Athlete.objects.all()
    if options['username']:
      users = users.filter(username=options['username'])

    users = users.order_by('username')

    cal = calendar.Calendar()

    for user in users:
      print(user)

      # Search first active day
      first = SportDay.objects.filter(week__user=user).order_by('date').first()
      if not first:
        print(' !! No day, no stats !!')
        continue

      # Buil StatsMonth until now
      for year in range(first.date.year, today.year+1):
        print(year)
        for month in range(1, 13):

          # Skip unecessary months (no data)
          if (year, month) < (first.date.year, first.date.month) or (year, month) > (today.year, today.month):
            continue

          # Build StatsMonth
          stats = StatsMonth(user, year, month)
          stats.build()

          # Build weeks
          weeks = cal.monthdatescalendar(year, month)
          for w in weeks:
            day = w[0]
            if day.month != month:
              continue
            week = int(day.strftime('%W'))
            stats = StatsWeek(user, year, week)
            stats.build()
