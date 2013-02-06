from helpers import render
from django.contrib.auth.decorators import login_required
from models import RunReport, RunSession
from datetime import date
from forms import RunSessionFormSet

@login_required
@render('run/index.html')
def index(request):

  # Init current report
  today = date.today()
  week = int(today.strftime('%W'))
  report, created = RunReport.objects.get_or_create(user=request.user, year=today.year, week=week)
  if created:
    report.init_sessions()

  # Build formset
  sessions = report.sessions.all().order_by('date')
  if request.method == 'POST':
    form = RunSessionFormSet(request.POST)
    if form.is_valid():
      form.save()
  else:
    form = RunSessionFormSet(queryset=sessions)

  return {
    'report' : report,
    'form' : form,
  }
