from django.views.generic.list import ListView
from page.models import Page



class PageList(ListView):
  model = Page
  template_name = 'page/list.html'
