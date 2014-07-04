from mixins import ClubMixin
from sport.views import SportStats

class ClubMemberStats(ClubMixin, SportStats):

  def get_url_context(self):
    # Gives club url context
    return {
      'url_base' : 'club-member-stats',
      'url_args' : [self.club.slug, self.member.username],
    }
