from django.core.urlresolvers import reverse
from runreport.mixins import LoginRequired
from gear.forms import GearItemForm


class GearMixin(LoginRequired):
  '''
  Common mixin for gear management
  '''
  context_object_name = 'gear'
  form_class = GearItemForm

  def get_queryset(self):
    return self.request.user.items.all()

  def get_success_url(self):
    return reverse('gear')

  def form_valid(self, form):
    # Save with user
    gear = form.save(commit=False)
    gear.user = self.request.user
    gear.save()

    return super(GearMixin, self).form_valid(form)
