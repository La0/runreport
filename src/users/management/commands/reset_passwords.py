from django.core.management.base import BaseCommand, CommandError
from users.models import Athlete
from django.conf import settings
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('password', type=str, nargs='?', default='plop')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                'This command should not be run in production !')
        self.reset(options['password'])

    def reset(self, password):
        password_hash = make_password(password)
        athletes = Athlete.objects.all()
        athletes.update(password=password_hash)
        print(
            'Resetted %s accounts with password %s' %
            (athletes.count(), password))
