from mixins import ClubManagerMixin
from django.views.generic.edit import UpdateView, CreateView, BaseDeleteView
from club.models import Club, ClubLink
from club.forms import ClubCreateForm, ClubLinkForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from coach.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE
from django.db.models import Max

class ClubManage(ClubManagerMixin, UpdateView):
  model = Club
  template_name = "club/manage.html"
  form_class = ClubCreateForm

  def form_valid(self, form):
    club = form.save()
    self.club = club
    return HttpResponseRedirect(reverse('club-manage', kwargs={'slug' : self.club.slug}))

  def get_context_data(self, *args, **kwargs):
    context = super(ClubManage, self).get_context_data(*args, **kwargs)
    context['stats'] = self.club.load_stats()
    context['links'] = self.club.links.all().order_by('name')
    return context

class ClubLinkAdd(ClubManagerMixin, JsonResponseMixin, CreateView):
  model = ClubLink
  template_name = "club/link/add.html"
  form_class = ClubLinkForm

  def form_valid(self, form):
    '''
    Save link on last position
    '''
    link = form.save(commit=False)
    link.club = self.club
    max_pos = self.club.links.all().aggregate(Max('position'))
    link.position = (max_pos['position__max'] or 0) + 1
    link.save()

    # Reload & don't render
    self.json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE]

    return self.render_to_response(self.get_context_data(**{'form' : form}))

class ClubLinkDelete(ClubManagerMixin, JsonResponseMixin, BaseDeleteView):
  model = ClubLink

  def get_success_url(self):
    return reverse('club-manage', args=(self.club.slug, ))

  def get_object(self):
    try:
      self.link = self.model.objects.get(pk=self.kwargs['id'], club=self.club) 
    except:
      raise Exception("No link found")

    return self.link
