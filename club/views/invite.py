from club.models import ClubInvite
from club.forms import InviteAskForm
from users.models import Athlete
from django.views.generic import DetailView, RedirectView
from django.http import Http404
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView

class ClubInviteCheck(RedirectView, DetailView):
  model = ClubInvite

  def get_redirect_url(self, *args, **kwargs):
    self.invite = self.get_object()
    # Check invite is not already used
    if self.invite.used:
      raise Http404("Invite used.")

    # Save invite in session
    self.request.session['invite'] = self.invite.slug

    # If user is not connected
    if not self.request.user.is_authenticated():
      try:
        # Redirect to login if account exists
        Athlete.objects.get(email=self.invite.recipient)
        return reverse('login')
      except Athlete.DoesNotExist, e:
        # Redirect to account creation
        return reverse('user-create')

    # User is connected, redirect to club creation
    return reverse('club-create')

class ClubInviteAsk(CreateView):
  template_name = 'club/ask_invite.html'
  model = ClubInvite
  form_class = InviteAskForm

  def form_valid(self, form):
    invite = form.save(commit=False)
    invite.type = 'create' # Only use club creation
    invite.sender = Athlete.objects.get(username='inviter')
    invite.save()

    return self.render_to_response({'form': form, 'asked' : True})
