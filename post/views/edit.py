from django.views.generic import UpdateView, CreateView, ListView
from .mixins import PostWriterMixin


class PostListView(PostWriterMixin, ListView):
  context_object_name = 'posts'
  template_name = 'post/list.html'

class PostCreateView(PostWriterMixin, CreateView):
  pass

class PostEditView(PostWriterMixin, UpdateView):
  pass
