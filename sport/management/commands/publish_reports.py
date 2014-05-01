from django.core.management.base import BaseCommand, CommandError
from datetime import date
from sport.models import SportWeek

class Command(BaseCommand):

  def handle(self, *args, **options):
    '''
    Publish all reports for this week
    '''
    year, week = self.get_current_week()
    reports = SportWeek.objects.filter(year=year, week=week, published=False).order_by('user__username')
    reports = reports.filter(user__auto_send=True) # Auto send must be enabled per user
    for r in reports:

      # Skip empty report
      sessions = r.sessions.exclude(comment=None)
      if sessions.count() == 0:
        print 'No active sessions for report %s' % r
        continue

      # Publish
      for m in r.user.memberships.all():
        r.publish(m, 'https://runreport.fr') # TODO : use a config
      print 'Published %s' % r

  def get_current_week(self):
    today = date.today()
    return today.year, int(today.strftime('%W'))
