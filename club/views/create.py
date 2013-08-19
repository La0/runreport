from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from club.models import Club, ClubMembership
from club.forms import ClubCreateForm
from django.core.urlresolvers import reverse
from mixins import ClubCreateMixin

class ClubCreate(ClubCreateMixin, CreateView):
  model = Club
  template_name = 'club/create.html'
  form_class = ClubCreateForm

  def form_valid(self, form):
    # Create club
    club = form.save(commit=False)
    club.manager = self.request.user
    club.save()

    # Setup user as staff member
    ClubMembership.objects.create(club=club, user=self.request.user, role="staff")

    # Use invite
    self.invite.use()
    del self.request.session['invite']

    return HttpResponseRedirect(reverse('club-manage', kwargs={'slug' : club.slug}))
