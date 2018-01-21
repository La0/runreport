from django.views.generic import DeleteView
from .mixins import PostMediaMixin
from runreport.mixins import JsonResponseMixin


class PostMediaDeleteView(PostMediaMixin, JsonResponseMixin, DeleteView):
    template_name = 'post/media.delete.html'
