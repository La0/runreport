from django.views.generic import TemplateView
from django.http import Http404

class FeaturesView(TemplateView):
  '''
  Render static html features page
  '''
  def get_template_names(self):
    pages = ('home', 'runner', 'trainer', )
    page = self.kwargs.get('page', 'home')
    if page not in pages:
      raise Http404()
    return 'features/%s.html' % page
