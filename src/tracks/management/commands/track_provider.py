from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from users.models import Athlete
from tracks.providers import get_provider


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--username',
                    action='store',
                    dest='username',
                    type='string',
                    default=False,
                    help='Ran the import on the specified user.',
                    ),
        make_option('--provider',
                    action='store',
                    dest='provider',
                    type='string',
                    default=False,
                    help='Ran the import with this provider.',
                    ),
        make_option('--full',
                    action='store_true',
                    dest='full',
                    default=False,
                    help='Run a full import on user, don\'t skip any track.',
                    ),
        make_option('--list',
                    action='store_true',
                    dest='list',
                    default=False,
                    help='List all tracks on a user, from provider.',
                    ),
    )
    user = None
    provider = None

    def handle(self, *args, **options):
        # Check input
        if not options['username']:
            raise CommandError("Missing username")
        if not options['provider']:
            raise CommandError("Missing provider")

        # Load user
        try:
            self.user = Athlete.objects.get(username=options['username'])
            print(
                'User #%d %s %s' %
                (self.user.id,
                 self.user.first_name,
                 self.user.last_name))
        except Exception as e:
            raise CommandError(
                "Invalid user %s : %s" %
                (options['username'], str(e)))

        # Load provider
        self.provider = get_provider(options['provider'], self.user)
        if not self.provider:
            raise CommandError("Invalid provider %s" % options['provider'])

        # Check connectivity
        if not self.provider.is_connected():
            raise CommandError(
                "Provider %s is not connected for user %s" %
                (self.provider.NAME, self.provider.user))

        if options['list']:
            # List tracks
            self.provider.debug_tracks()

        else:
            # Run the import
            self.provider.import_user(options['full'])
