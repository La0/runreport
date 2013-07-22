from mixins import ClubManagerMixin
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

  def load_stats(self):
    '''
    Count available and used accounts
    '''
    stats = []
    types = ('staff', 'trainer', 'athlete')
    for t in types:
      max = getattr(self.club, 'max_%s' % t)
      used = self.club.clubmembership_set.filter(role=t).count()
      stats.append({
        'type' : t,
        'max' : max,
        'used' : used,
        'diff' : max - used,
        'percent' : round(100 * (max - used) / max)
      })
    return stats

  def get_context_data(self, *args, **kwargs):
    context = super(ClubManage, self).get_context_data(*args, **kwargs)
    context['stats'] = self.load_stats()
    context['links'] = self.club.links.all().order_by('name')
    context['invites'] = self.club.invites.all().order_by('created')
    return context
