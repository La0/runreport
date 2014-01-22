from mixins import ClubMixin
from django.views.generic import ListView
from run.models import RunSession
from club.models import ClubMembership
from datetime import date

class ClubRaces(ClubMixin, ListView):
  template_name = 'club/races.html'
  model = RunSession
  context_object_name = 'races'

  def get_queryset(self):
    # Fetch my athletes
    # TODO: put in query manager
    users = [m.user for m in ClubMembership.objects.filter(club=self.club, trainers=self.request.user, role='athlete')]

    return self.model.objects.filter(type='race', date__gte=date.today(), report__user__in=users).order_by('date', 'report__user__first_name')
