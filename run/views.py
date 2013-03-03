from helpers import render
from django.contrib.auth.decorators import login_required
from models import RunReport, RunSession
from datetime import date, datetime, timedelta
from forms import RunSessionFormSet, RunReportForm
from django.http import Http404, HttpResponse
from coach.settings import REPORT_START_DATE
import calendar

@render('run/index.html')
def report(request, year=False, week=False):
  if not request.user.is_authenticated():
    return {}

  # Load min date
  min_year, min_week = REPORT_START_DATE
  dt = datetime.strptime('%d %d 1' % (min_year, min_week), '%Y %W %w')
  min_date = dt.date()

  today = date.today()
  today_week = int(today.strftime('%W'))
  report_date = None
  if not year or not week:
    # Use current week by default
    week = today_week
    year = today.year
    report_date = today

  else:
    # Check week is valid
    year = int(year)
    week = int(week)
    dt = datetime.strptime('%d %d 1' % (year, week), '%Y %W %w')
    report_date = dt.date()
    if report_date < min_date:
      raise Http404('Too old.')
    if report_date > today:
      raise Http404('In the future.')

  # Init report
  report, created = RunReport.objects.get_or_create(user=request.user, year=year, week=week)
  if created:
    report.init_sessions()

  # Build formset
  form, form_report = None, None
  sessions = report.sessions.all().order_by('date')
  if not report.published:
    if request.method == 'POST':
      # Save comments
      form = RunSessionFormSet(request.POST)
      if form.is_valid():
        form.save()

      # Sace report
      form_report = RunReportForm(request.POST, instance=report)
      if form_report.is_valid():
        form_report.save()

      # Publish ?
      if request.POST['action'] == 'publish':
        report.publish()
    else:
      form = RunSessionFormSet(queryset=sessions)
      form_report = RunReportForm(instance=report)

  # Get profile
  profile = request.user.get_profile()

  # Build weeks for pagination
  weeks = []
  dt = min_date
  i, current_pos = 0, 0
  while dt < today:
    current = (dt == report_date)
    if current:
      current_pos = i
    weeks.append({
      'start' : dt,
      'end'   : dt + timedelta(days=6),
      'current' : current,
      'week'  : dt.strftime('%W'),
      'year'  : dt.year,
    })
    dt += timedelta(days=7)
    i += 1

  week_previous = current_pos - 1 > 0 and weeks[current_pos - 1] or None
  week_next = current_pos + 1 < len(weeks) and weeks[current_pos + 1] or None

  # Get previous report if not published
  report_previous = None
  if report.is_current() and week_previous:
    try:
      report_previous = RunReport.objects.get(user=request.user, week=week_previous['week'], published=False)
    except:
      pass

  return {
    'report' : report,
    'report_previous' : report_previous,
    'profile' : profile,
    'sessions': sessions,
    'form' : form,
    'form_report' : form_report,
    'trainer' : profile.trainer,
    'now' : datetime.now(),
    'weeks': weeks,
    'week_previous' : week_previous,
    'week_next' : week_next,
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
def month(request, year=False, month=False):
  # Setup current month
  today_month = datetime.now().replace(day=1) 
  current_month = (month and year) and datetime.strptime('%s %s 1' % (year, month), '%Y %m %d') or today_month

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

@login_required
@render('run/vma.html')
def vma(request):
  from vma import VmaCalc

  profile = request.user.get_profile()

  vma = VmaCalc(profile.vma)

  return {
    'profile' : profile,
    'vma' : vma
  }
