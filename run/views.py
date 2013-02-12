from helpers import render
from django.contrib.auth.decorators import login_required
from models import RunReport, RunSession
from datetime import date
from forms import RunSessionFormSet
from django.http import Http404, HttpResponse

@render('run/index.html')
def index(request):
  if not request.user.is_authenticated():
    return {}

  # Init current report
  today = date.today()
  week = int(today.strftime('%W'))
  report, created = RunReport.objects.get_or_create(user=request.user, year=today.year, week=week)
  if created:
    report.init_sessions()

  # Build formset
  form = None
  sessions = report.sessions.all().order_by('date')
  if not report.published:
    if request.method == 'POST':
      # Save comments
      form = RunSessionFormSet(request.POST)
      if form.is_valid():
        form.save()

      # Publish ?
      if request.POST['action'] == 'publish':
        report.publish()
    else:
      form = RunSessionFormSet(queryset=sessions)

  # Get profile
  profile = request.user.get_profile()

  return {
    'report' : report,
    'sessions': sessions,
    'form' : form,
    'trainer' : profile.trainer,
    'today' : date.today(),
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
