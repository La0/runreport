from django.views.generic.detail import DetailView
from page.models import Page
from page.forms import PageForm
from mixins import PageMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.http import Http404

class PageDetail(PageMixin, ModelFormMixin, ProcessFormView, DetailView):
  model = Page
  template_name = 'page/detail.html'
  form_class = PageForm

  def get_form(self, form_class):
    # Load object before form init
    if not hasattr(self, 'object'):
      self.get_object()
    return super(PageDetail, self).get_form(form_class)

  def get_object(self):
    filters = {
      'type' : self.type,
      'slug' : self.kwargs['slug'],
    }
    if not self.edit:
      filters['published'] = True
    try:
      self.object = Page.objects.get(**filters)
    except Exception, e:
      if not self.edit:
        raise Http404('No page found')

      # Create new page
      self.object = Page(**filters)
      self.object.name = self.kwargs['slug'].capitalize()
      self.object.user = self.request.user
    return self.object
