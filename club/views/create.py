from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from club.models import Club
from club.forms import ClubCreateForm
from django.core.urlresolvers import reverse
from mixins import ClubCreateMixin

class ClubCreate(ClubCreateMixin, CreateView):
  model = Club
  template_name = 'club/create.html'
  form_class = ClubCreateForm

  def form_valid(self, form):
    club = form.save(commit=False)
    club.manager = self.request.user
    club.save()
    return HttpResponseRedirect(reverse('club-manage', args=[club]))
