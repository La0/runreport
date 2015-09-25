from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from club.models import Club, ClubMembership
from club.forms import ClubCreateForm
from django.conf import settings
from django.core.urlresolvers import reverse
from mixins import ClubCreateMixin
from runreport.mixins import LoginRequired

class ClubCreate(LoginRequired, ClubCreateMixin, CreateView):
  model = Club
  template_name = 'club/create.html'
  form_class = ClubCreateForm

  def get_initial(self):
    return {
      'phone' : self.request.user.phone,
    }

  def form_valid(self, form):
    # Create club
    club = form.save(commit=False)
    club.manager = self.request.user
    club.save()

    # Set phone on user
    self.request.user.phone = form.cleaned_data['phone']
    self.request.user.save()

    # Setup user as staff member
    ClubMembership.objects.create(club=club, user=self.request.user, role="trainer")

    # Use invite
    if not settings.CLUB_CREATION_OPEN :
      self.invite.use(club)
      del self.request.session['invite']

    return HttpResponseRedirect(reverse('club-manage', kwargs={'slug' : club.slug}))
