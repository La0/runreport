from django.core.management.base import BaseCommand, CommandError
from datetime import date
from run.models import RunReport

class Command(BaseCommand):

  def handle(self, *args, **options):
    '''
    Publish all reports for this week
    '''
    year, week = self.get_current_week()
    reports = RunReport.objects.filter(year=year, week=week, published=False).order_by('user__username')
    reports = reports.filter(user__userprofile__auto_send=True) # Auto send must be enabled per user
    for r in reports:

      # Skip empty report
      sessions = r.sessions.exclude(comment=None)
      if sessions.count() == 0:
        print 'No active sessions for report %s' % r
        continue

      # Publish
      r.publish()
      print 'Published %s' % r

  def get_current_week(self):
    today = date.today()
    return today.year, int(today.strftime('%W'))
