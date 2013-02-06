from helpers import render
from django.contrib.auth.decorators import login_required
from models import RunReport, RunSession
from datetime import date
from forms import RunSessionFormSet
from django.http import Http404, HttpResponse

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

@login_required
def excel(request, year, week):
  print year, week
  try:
    report = RunReport.objects.get(user=request.user, year=int(year), week=int(week))
  except:
    raise Http404('Report not found')

  excel = report.build_xls()

  response = HttpResponse(open(excel), content_type='application/vnd.ms-excel')
  response['Content-Disposition'] = 'attachment; filename="%s_semaine_%s.xls"' % (request.user.username, report.week)
  return response
