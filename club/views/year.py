from run.views import RunCalendarYear
from mixins import ClubMixin

class ClubMemberYear(ClubMixin, RunCalendarYear):

  def get_user(self):
    return self.member

  def get_links(self):
    return {
      'pageargs' : [self.club.slug, self.member.username, ],
      'pageyear' : 'club-member-year',
      'pagemonth' : 'club-member-month',
      'pageday' : 'club-member-day',
    }
