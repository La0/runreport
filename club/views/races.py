from mixins import ClubMixin
from django.views.generic import ListView, TemplateView
from sport.models import SportSession
from club.models import ClubMembership
from datetime import date
from sport.views.mixins import AthleteRaces

class ClubRaces(ClubMixin, ListView):
  template_name = 'club/races.html'
  model = SportSession
  context_object_name = 'races'

  def get_queryset(self):
    # Fetch my athletes
    # TODO: put in query manager
    users = [m.user for m in ClubMembership.objects.filter(club=self.club, trainers=self.request.user, role='athlete')]

    # Add myself to view my races
    users.append(self.request.user)

    races = self.model.objects.filter(type='race', day__date__gte=date.today(), day__week__user__in=users)
    races = races.order_by('day__date', 'day__week__user__first_name')
    return races



class ClubMemberRaces(ClubMixin, AthleteRaces, TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self, *args, **kwargs):
    context = super(ClubMemberRaces, self).get_context_data(*args, **kwargs)

    # Add url parameters to see reports
    context.update({
      'raceurl' : 'user-calendar-day',
      'raceargs' : [self.member.username],
    })
    return context
