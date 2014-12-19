from django.views.generic import UpdateView, CreateView
from .mixins import PostWriterMixin

class PostCreateView(PostWriterMixin, CreateView):
  pass

class PostEditView(PostWriterMixin, UpdateView):
  pass
