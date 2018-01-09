from .mixins import ProfilePrivacyMixin
from sport.views import SportStats


class AthleteStats(ProfilePrivacyMixin, SportStats):
    rights_needed = ('stats', )

    def get_url_context(self):
        # Gives club url context
        return {
            'url_base': 'athlete-stats',
            'url_month': 'user-calendar-month',
            'url_args': [self.member.username],
        }
