from django.views.generic import TemplateView
from coach.features import list_features

class FeaturesView(TemplateView):
  template_name = 'features.html'

  def get_context_data(self, *args, **kwargs):
    context = super(FeaturesView, self).get_context_data(*args, **kwargs)
    context.update(list_features())
    return context
