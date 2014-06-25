from django.core.management.base import BaseCommand, CommandError
from sport.models import SportDay, SportSession, Sport
import time

class Command(BaseCommand):
  fields = (
    'name',
    'comment',
    'time',
    'distance',
    'type',
    'race_category',
  )

  def handle(self, *args, **options):
    days = SportDay.objects.all().order_by('date')
    sport = Sport.objects.get(slug='running')
    for i, day in enumerate(days):
      print '%d/%d %s %s' % (i, days.count(), day.date, day.week.user.username)

      if day.sessions.count() >= 1:
        # Keep user input on best session
        self.match_sessions(day)
      else:
        # Init session with running
        SportSession.objects.create(day=day, sport=sport, time=day.time, distance=day.distance, name=day.name, comment=day.comment, type=day.type, race_category=day.race_category)
        print ' > Create running SportSession'

  def match_sessions(self, day):
    '''
    Match the data from a day to
    multiple sessions, by picking out the best
    '''
    def tstamp(t):
      return t.hour * 3600 + t.minute * 60 + t.second

    min_dist = float('inf')
    best_session = None

    # Debug
    #print '-' * 80
    #print 'Day #%d "%s" %s %s' % (day.pk, day.name, day.time, day.distance)

    for session in day.sessions.all():
    #  print 'Session #%d "%s" %s %s %s' % (session.pk, session.name, session.sport, session.time, session.distance)
      
      # Search for closest session
      dist = 0.0
      if day.distance and session.distance:
        dist += abs(day.distance - session.distance)
      if day.time and session.time:  
        dist += abs(tstamp(day.time) - tstamp(session.time))
      if dist < min_dist:
        best_session = session
        min_dist = dist

    print ' >> Best Session is #%d' % (best_session.pk)

    # Apply changes
    modified = False
    for field in self.fields:
      user_val = getattr(day, field)
      if getattr(best_session, field) != user_val:
        setattr(best_session, field, user_val)
        modified = True
    if modified:
      best_session.save()
    print ' > Update existing running SportSession'

