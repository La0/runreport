from __future__ import absolute_import

from celery import shared_task


@shared_task
def auto_publish_reports(*args, **kwargs):
    '''
    Publish all reports for this week
    '''
    from datetime import date, timedelta
    from sport.models import SportWeek
    from django.db.models import Count
    from helpers import date_to_week
    # just to be sure we don't send the next week !
    today = date.today() - timedelta(days=1)
    week, year = date_to_week(today)
    reports = SportWeek.objects.filter(
        year=year, week=week, published=False).order_by('user__username')
    # Auto send must be enabled per user
    reports = reports.filter(user__auto_send=True)
    roles = ('athlete', 'trainer', 'staff', )
    for r in reports:

        # Skip empty report
        agg = r.days.aggregate(nb=Count('sessions'))
        if not agg['nb']:
            print('No active sessions for report %s' % r)
            continue

        # Publish
        for m in r.user.memberships.filter(role__in=roles):
            r.publish(m, 'https://runreport.fr')  # TODO : use a config
        print('Published %s' % r)


@shared_task
def publish_report(report, membership, uri):
    '''
    Publish a report: build mail with XLS, send it.
    '''
    report.publish(membership, uri)


@shared_task
def sync_session_gcal(session, delete=False):
    '''
    Sync a SportSession on Google calendar
    '''
    from sport.gcal import GCalSync

    # Check the user has gcal
    user = session.day.week.user
    if not user.has_gcal():
        return

    # Start sync
    gc = GCalSync(user)
    if delete and session.gcal_id:
        gc.delete_event(session.gcal_id)
    else:
        gc.sync_sport_session(session)


@shared_task
def sync_gcal(user):
    '''
    Sync all the user sport sessions
    when creating a new calendar
    '''
    if not user.has_gcal():
        return

    from sport.gcal import GCalSync
    from sport.models import SportSession

    sessions = SportSession.objects.filter(day__week__user=user)
    sessions = sessions.filter(gcal_id__isnull=True)
    sessions = sessions.order_by('-day__date')

    gc = GCalSync(user)
    for s in sessions:
        try:
            gc.sync_sport_session(s)
        except Exception as e:
            print('Failed to create an event: %s' % (str(e), ))


@shared_task
def race_mail(*args, **kwargs):
    '''
    Send a mail to all users having a race today
    '''
    from sport.models import SportSession
    from datetime import date, timedelta
    from runreport.mail import MailBuilder

    # Setup mail builder
    builder = MailBuilder('mail/race.html')

    # Load tommorow's race
    tmrw = date.today() + timedelta(days=1)
    races = SportSession.objects.filter(day__date=tmrw, type='race')

    # Build and Send all mails
    for race in races:
        user = race.day.week.user
        data = {
            'race': race,
            'user': user,
        }
        builder.language = user.language
        builder.subject = u'Votre course %s - RunReport' % (race.name,)
        builder.to = [user.email, ]
        mail = builder.build(data)
        mail.send()
