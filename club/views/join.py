from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from club.models import Club, ClubMembership
from runreport.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD, JSON_OPTION_ONLY_AJAX
from django.core.exceptions import PermissionDenied

class ClubList(ListView):
  model = Club
  template_name = 'club/join.html'
  context_object_name = 'clubs'

  def get_queryset(self):
    # List normal clubs
    club_ids = [c['pk'] for c in Club.objects.exclude(demo=True).exclude(private=True).values('pk')]

    # Add user's clubs
    if self.request.user.is_authenticated():
      club_ids += [c['club__pk'] for c in self.request.user.memberships.values('club__pk')]

    # Add club from session (from user without auth first)
    if 'club_join' in self.request.session:
      club_id, club_secret = self.request.session['club_join']
      club_ids += [club_id, ]

    # Load club queryset
    clubs = Club.objects.filter(pk__in=club_ids)
    clubs = clubs.prefetch_related('clubmembership_set')
    clubs = clubs.order_by('name')

    return clubs

class ClubJoin(JsonResponseMixin, TemplateView, ):
  template_name = 'club/joined.html'
  json_template_name = 'club/joined.modal.html'
  json_options = [JSON_OPTION_ONLY_AJAX, ]

  def check_access(self):
    self.club = get_object_or_404(Club, slug=self.kwargs['slug'])

    # Check hash from GET args or session
    if self.club.private:
      secret = self.kwargs.get('secret', None)
      if not secret:
        _, secret = self.request.session.get('club_join', (None, None))
      if self.club.get_private_hash() != secret:
        raise PermissionDenied

  def get_context_data(self, *args, **kwargs):
    # Check access for private clubs
    self.check_access()
    context = {
      'club' : self.club,
    }

    # When user is not connected:
    # * save club & hash in session
    # * display an helpful message
    if not self.request.user.is_authenticated():
      self.request.session['club_join'] = (self.club.pk, self.kwargs.get('secret', None))
      context['error'] = 'logout'
      return context

    # Check there is no existing relation
    if self.club.has_user(self.request.user):
      context['error'] = 'member'
      return context

    # Create new membership
    member = ClubMembership.objects.create(club=self.club, user=self.request.user, role='prospect')

    # Send notification to manager
    try:
      member.mail_club()
    except Exception, e:
      print 'Notification failed : %s' % (str(e), )
      # Don't keep membership when no mail is sent
      member.delete()
      context['error'] = 'mail'

    # Cleanup session
    if 'club_join' in self.request.session:
      del self.request.session['club_join']

    return context
