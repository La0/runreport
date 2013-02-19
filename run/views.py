from helpers import render
from django.contrib.auth.decorators import login_required
from models import RunReport, RunSession
from datetime import date, datetime, timedelta
from forms import RunSessionFormSet
from django.http import Http404, HttpResponse
import calendar

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
        report.updated = datetime.now()
        report.save()

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
    'now' : datetime.now(),
  }

@login_required
def excel(request, year, week):
  try:
    report = RunReport.objects.get(user=request.user, year=int(year), week=int(week))
  except:
    raise Http404('Report not found')

  excel = report.build_xls()

  response = HttpResponse(open(excel), content_type='application/vnd.ms-excel')
  response['Content-Disposition'] = 'attachment; filename="%s_semaine_%s.xls"' % (request.user.username, report.week)
  return response

@login_required
@render('run/month.html')
def month(request, year, month=False):
  # Setup current month
  today_month = datetime.now().replace(day=1) 
  current_month = month and datetime.strptime('%s %s 1' % (year, month), '%Y %m %d') or today_month

  # Load all days & weeks for this month
  try:
    cal = calendar.Calendar(calendar.MONDAY)
    days = [d for d in cal.itermonthdates(current_month.year, current_month.month)]
    weeks = cal.monthdatescalendar(current_month.year, current_month.month)
  except Exception, e:
    raise Http404(str(e))

  # Load all sessions for this month
  sessions = RunSession.objects.filter(report__user=request.user, date__in=days)
  sessions = dict((r.date, r) for r in sessions)

  # Months first days
  previous_month = current_month - timedelta(days=20)
  next_month = current_month.date() < today_month.date() and current_month + timedelta(days=40) or None

  return {
    'months' : (previous_month, current_month, next_month),
    'days': days,
    'weeks' : weeks,
    'sessions' : sessions,
  }
