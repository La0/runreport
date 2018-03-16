from django.views.generic.detail import DetailView
from page.models import Page
from .mixins import PageMixin
from django.http import Http404


class PageDetail(PageMixin, DetailView):
    model = Page
    template_name = 'page/detail.html'

    def get_object(self):
        filters = {
            'type': self.type,
            'slug': self.kwargs['slug'],
            'published': True,
        }
        try:
            self.object = Page.objects.get(**filters)
        except Page.DoesNotExist:
            raise Http404('No page found')
        return self.object
