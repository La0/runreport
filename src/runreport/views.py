from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
import os

class PricingView(TemplateView):
  '''
  Display all prices in a single page
  '''
  template_name = 'landing/pricing.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PricingView, self).get_context_data(*args, **kwargs)

    context['prices'] = settings.PREMIUM_PRICES

    return context

class LegalView(TemplateView):
  template_name = 'legal.html'

  def get_context_data(self, *args, **kwargs):
    context = super(LegalView, self).get_context_data(*args, **kwargs)

    # Load html
    type = self.kwargs['type']
    context['type'] = type
    path = os.path.join(settings.SRC, 'legal/%s.html' % type)
    if not os.path.exists(path):
      raise Http404('Legal page not found %s' % type)
    with open(path, 'r') as f:
      context['legal_html'] = f.read()

    return context
