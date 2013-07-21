from mixins import ClubManagerMixin
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from club.models import Club
from club.forms import ClubCreateForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class ClubManage(ClubManagerMixin, UpdateView):
  model = Club
  template_name = "club/manage.html"
  form_class = ClubCreateForm

  def form_valid(self, form):
    club = form.save()
    self.club = club
    return HttpResponseRedirect(reverse('club-manage', kwargs={'slug' : self.club.slug}))

