from django.views.generic.list import ListView
from page.models import Page
from mixins import PageMixin

class PageList(PageMixin, ListView):
  model = Page
  template_name = 'page/list.html'
  context_object_name = 'pages'

  def get_queryset(self):
    pages = Page.objects.filter(type=self.type).order_by('-updated')
    if not self.edit:
      pages = pages.exclude(published=False)
    return pages
