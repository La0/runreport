from django.core.management.base import BaseCommand, CommandError
from datetime import date
from run.models import RunReport

class Command(BaseCommand):

  def handle(self, week, year, *args, **options):
    '''
    Publish all reports for this week
    '''
    site = 'https://runreport.fr' # Should be a setting now that sites are gone
    reports = RunReport.objects.filter(year=year, week=week, published=True).order_by('user__username')
    for report in reports:
      print report
      for member in report.user.memberships.all():
        print ' > %s' % member.club
        report.published = False
        report.publish(member, site)
