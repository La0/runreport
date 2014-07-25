# encoding: utf-8
from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from sport.models import SportSession, SportDay, SportWeek
from datetime import datetime, timedelta
import random
from helpers import date_to_week

class Command(BaseCommand):
  days_past = 150
  days_future = 10
  today = None

  # Comments to not use those from users
  comments = [
    u'Bonne séance',
    u'Dur sous la pluie',
    u'Très agréable',
    u'Bonnes sensations, à refaire !',
    u'Il faisait trop chaud !',
  ]

  def handle(self, *args, **options):

    # List days needed
    self.today = datetime.now()
    start = self.today - timedelta(days=self.days_past)
    days = [(start + timedelta(days=i)).date() for i in range(0, self.days_past + self.days_future)]

    # Build days
    for a in Athlete.objects.filter(demo=True):
      self.build_days(a, days)

  def build_days(self, user, days):
    print 'Setup demo for %s' % user

    # Remove all days / week
    user.sportweek.all().delete()

    # Build every day with a probability
    # stronger on weekends
    for day in days:
      min_prob = day.weekday() < 5 and 0.3 or 0.6
      if random.random() > min_prob:
        continue
      self.build_day(user, day)

  def build_day(self, user, day):
    # Build new week/day chain
    w,y = date_to_week(day)
    published = day < (self.today - timedelta(days=6)).date()
    week,_ = SportWeek.objects.get_or_create(user=user, week=w, year=y, defaults={'published':published,})
    d,_ = SportDay.objects.get_or_create(week=week, date=day)

    # Build random number of session
    # with a higher chance to get 1 session per day
    for i in range(0, random.choice([1,1,1,1,1,1,1,2,2,3])):
      self.build_session(d)


  def build_session(self, sport_day):
    # Pick a random SportSession
    week_day = int(sport_day.date.strftime('%w')) + 1 # special format for django orm (1 is sunday)
    rand_session = SportSession.objects.filter(name__isnull=False, day__date__week_day=week_day).order_by('?').first()

    # Build session
    session_data = {
      'day' : sport_day,
      'name' : rand_session.name,
      'type' : rand_session.type,
      'sport' : rand_session.sport,
      'race_category' : rand_session.race_category,
    }
    print sport_day.date, rand_session.sport

    # No distance, comment or time for future
    if sport_day.date < self.today.date():
      session_data.update({
        'time' : rand_session.time,
        'distance' : rand_session.distance,
        'comment' : random.choice(self.comments),
      })
    session = SportSession.objects.create(**session_data)
