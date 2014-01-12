from django.core.management.base import BaseCommand, CommandError
from run.models import RunReport

class Command(BaseCommand):
  year = 2014
  def handle(self, *args, **options):

    reports = RunReport.objects.filter(year=self.year, week=0).order_by('user__username')
    for r in reports:
      self.patch_report(r)

  def patch_report(self, report_source):

    # Get report dest just before
    report_dest,_ = RunReport.objects.get_or_create(user=report_source.user, year=self.year - 1, week=52)

    print "%s >> %s" % (report_source, report_dest)

    # Backup every session
    for sess_source in report_source.sessions.all():
      print ' > %s' % sess_source.date

      # Detect conflict
      try:
        sess_dest = report_dest.sessions.get(date=sess_source.date)
        sess_dest.delete()
      except Exception, e:
        pass # Go on...

      sess_source.report = report_dest
      sess_source.save()

    # Update dest
    report_dest.calc_distance_time()
    report_dest.save()

    # Destroy source
    report_source.delete()
