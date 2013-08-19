from club.models import ClubInvite
from django.views.generic import DetailView, RedirectView
from django.http import Http404
from django.core.urlresolvers import reverse

class ClubInviteCheck(RedirectView, DetailView):
  model = ClubInvite

  def get_redirect_url(self, *args, **kwargs):
    self.invite = self.get_object()
    # Check invite is not already used
    if self.invite.used:
      raise Http404("Invite used.")

    # Save invite in session
    self.request.session['invite'] = self.invite.slug

    return reverse('club-create')
