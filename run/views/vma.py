from helpers import CoffinMixin
from django.views.generic import TemplateView
import json
from run.vma import VmaCalc

class VmaPaces(CoffinMixin, TemplateView):
  template_name = 'run/vma.html'

  def load_vma(self):
    profile = self.request.user.get_profile()
    vma = VmaCalc(profile.vma)

    return {
      'profile' : profile,
      'vma' : vma
    }

  def get_context_data(self, **kwargs):
    context = super(VmaPaces, self).get_context_data(**kwargs)
    context.update(self.load_vma())
    return context

class VmaGlossary(CoffinMixin, TemplateView):
  template_name = 'run/glossary.html'

  def load_glossary(self):
    with open('glossaire_vma.json', 'r') as f:
      glossary = json.loads(f.read())
      f.close()
    return {
      'glossary' : glossary,
      'sorted' : sorted(glossary),
    }

  def get_context_data(self, **kwargs):
    context = super(VmaGlossary, self).get_context_data(**kwargs)
    context.update(self.load_glossary())
    return context
