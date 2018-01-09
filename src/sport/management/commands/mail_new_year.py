# coding=utf-8
from django.core.management.base import BaseCommand
from sport.stats import StatsMonth
from sport.models import Sport
from users.models import Athlete
from datetime import date
from runreport.mail import MailBuilder

class Command(BaseCommand):
  def handle(self, *args, **options):
    # Get last year
    year = date.today().year - 1

    # Browse every athletes
    for athlete in Athlete.objects.all().order_by('username'):
      self.build_mail(year, athlete)

  def build_mail(self, year, user):
    print('Building mail for %d - %s' % (year, user))

    # Sum stats
    stats = {}
    for m in range(1, 13):
      month = StatsMonth(user, year, m)
      data = month.fetch()
      if data:
        stats = self.merge(stats, data)

    # Load sports objects
    if stats and 'sports' in stats:
      for s_id, s in stats['sports'].items():
        s['sport'] = Sport.objects.get(pk=s_id)

    # Build mail
    builder = MailBuilder('mail/new.year.html', user.language)

    data = {
      'year' : year,
      'stats' : stats,
      'user' : user,
    }
    builder.subject = u'[RunReport] Bonne année !'
    builder.to = [user.email, ]
    mail = builder.build(data)
    mail.send()

  def merge(self, x, y):
    '''
    Merge two dict
    '''
    for k,v in y.items():
      if isinstance(v, dict):
        x[k] = self.merge(x.get(k, {}), v)
      elif k in x and x[k] and v:
        x[k] += v
      else:
        x[k] = v

    return x
