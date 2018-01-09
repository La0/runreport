from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from plan.models import Plan
from sport.models import Sport
import arrow
import json


class Command(BaseCommand):
    """
    Import a plan from a standard json format
    """

    def add_arguments(self, parser):
        parser.add_argument('path', type=open, help='Plan path')
        parser.add_argument(
            '--user',
            type=str,
            action='append',
            help='Usernames to use the plan')

    def handle(self, *args, **options):

        # Load as json
        try:
            data = json.load(options['path'])
        except BaseException:
            raise CommandError('Not a json file')

        assert isinstance(data, dict)
        assert 'name' in data
        assert 'weeks' in data
        assert data.get('trainer'), \
            'No trainer in json'

        # Load trainer
        try:
            trainer = Athlete.objects.get(email=data['trainer'])
        except Athlete.DoesNotExist:
            raise CommandError('No trainer found: {trainer}'.format(**data))

        # Build a new plan
        plan = Plan(name=data['name'], creator=trainer)
        plan.start = min([arrow.get(w['start'])
                          for w in data['weeks']]).datetime
        plan.save()
        print('New plan #{} {}'.format(plan.pk, plan))

        # Only support running right now
        sport = Sport.objects.get(slug='running')

        # Build plan sessions
        for w, week in enumerate(data['weeks']):
            start = arrow.get(week['start'])
            for day in week['days']:
                offset = arrow.get(day['day']) - start
                session_data = {
                    'week': w,
                    'day': offset.days,
                    'name': day['title'],
                    'comment': day['content'],
                    'sport': sport,
                }
                session = plan.sessions.create(**session_data)
                print('New plan session {}'.format(session))

        # Publish to users
        users = Athlete.objects.filter(username__in=options.get('user', []))
        if users:
            plan.publish(users)
