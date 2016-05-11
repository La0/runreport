from page.models import PAGE_TYPES
from django.http import Http404

class PageMixin(object):
  def dispatch(self, request, *args, **kwargs):
    # Only an admin can edit
    self.edit = request.user.is_superuser

    # Load type
    if 'type' not in kwargs:
      raise Http404('No page type')
    self.type = kwargs['type']
    if self.type not in [p for p,_ in PAGE_TYPES]:
      raise Http404('Invalid page type')

    return super(PageMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(PageMixin, self).get_context_data(**kwargs)
    context['edit'] = self.edit
    context['type'] = self.type
    return context

