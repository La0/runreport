from django.views.generic import DetailView, RedirectView
from django.core.urlresolvers import reverse
from users.views.mixins import ProfilePrivacyMixin
from sport.views.mixins import AthleteRaces
from sport.views.stats import SportStatsMixin
from sport.models import SportSession
from datetime import date

class PublicProfile(ProfilePrivacyMixin, DetailView, SportStatsMixin, AthleteRaces):
  template_name = 'users/profile/index.html'
  context_object_name = 'member'

  def get_object(self):
    return self.member

  def get_context_data(self, *args, **kwargs):
    context = super(PublicProfile, self).get_context_data(*args, **kwargs)

    # Load calendar recent stats
    if 'calendar' in self.privacy:
      context.update(self.get_recent_stats())

    # Load races
    if 'races' in self.privacy or 'records' in self.privacy:
      context.update(self.get_races(self.member))

    # Load all stats
    if 'stats' in self.privacy:
      context.update(self.get_stats_months())

    return context

  def get_recent_stats(self):
    # Load last sessions
    today = date.today()
    sessions = SportSession.objects.filter(day__week__user=self.member, day__date__lte=today).order_by('-day__date')[:3]
    return {
      'today' : today,
      'last_sessions' : sessions,
    }

class OwnProfile(RedirectView):
  def get_redirect_url(self):
    # redirect to own profile
    return reverse('user-public-profile', args=(self.request.user.username, ))
