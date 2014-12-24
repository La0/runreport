from django.views.generic import UpdateView, CreateView, ListView
from .mixins import PostWriterMixin
from coach.mixins import JsonResponseMixin, JSON_OPTION_ONLY_AJAX


class PostListView(PostWriterMixin, ListView):
  context_object_name = 'posts'
  template_name = 'post/list.html'

class PostCreateView(PostWriterMixin, CreateView):
  pass

class PostEditView(PostWriterMixin, JsonResponseMixin, UpdateView):
  json_options = [JSON_OPTION_ONLY_AJAX, ]
