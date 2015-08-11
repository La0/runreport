from django.views.generic import DetailView, RedirectView
from django.core.urlresolvers import reverse
from django.db.models import Count, Max, Q
from users.views.mixins import ProfilePrivacyMixin
from sport.views.mixins import AthleteRaces
from sport.views.stats import SportStatsMixin
from sport.models import SportSession
from datetime import date
import operator


class PublicProfile(ProfilePrivacyMixin, DetailView, SportStatsMixin, AthleteRaces):
  template_name = 'users/profile/index.html'
  context_object_name = 'member'

  def get_object(self):
    return self.member

  def get_context_data(self, *args, **kwargs):
    context = super(PublicProfile, self).get_context_data(*args, **kwargs)

    # Always add badges
    context.update(self.get_last_badges())

    # Load calendar recent stats
    if 'calendar' in self.privacy:
      context.update(self.get_recent_stats())

    # Load races
    if 'races' in self.privacy or 'records' in self.privacy:
      context.update(self.get_races(self.member))

    # Load all stats
    if 'stats' in self.privacy:
      context.update(self.get_stats_months())

    # Add friend status
    if self.request.user != self.member and self.request.user.is_authenticated():
      context['friend_status'] = self.request.user.get_friend_status(self.member)

    return context

  def get_recent_stats(self, nb=3):
    # Load last sessions
    today = date.today()
    last_sessions = SportSession.objects.filter(day__week__user=self.member, day__date__lte=today)
    last_sessions = last_sessions.exclude(type='rest')
    last_sessions = last_sessions.order_by('-day__date')[:nb]

    # Load most commented
    commented_sessions = SportSession.objects.filter(day__week__user=self.member)
    commented_sessions = commented_sessions.exclude(comments_public__isnull=True)
    commented_sessions = commented_sessions.annotate(nb_comments=Count('comments_public__messages')).order_by('-nb_comments')[:nb]
    for c in commented_sessions:
      print c, c.nb_comments

    return {
      'today' : today,
      'last_sessions' : last_sessions,
      'commented_sessions' : commented_sessions,
    }

  def get_last_badges(self):
    # Load only the best badges of a user per category
    badges = self.member.badges.all()
    top_badges = badges.order_by().values('category_id').distinct().annotate(max_position=Max('position'))
    filters = reduce(operator.or_, [(Q(category_id=b['category_id']) & Q(position=b['max_position'])) for b in top_badges])
    badges = badges.filter(filters)

    return {
      'badges' : badges,
    }

class OwnProfile(RedirectView):
  permanent = False
  def get_redirect_url(self):
    # redirect to own profile
    return reverse('user-public-profile', args=(self.request.user.username, ))
