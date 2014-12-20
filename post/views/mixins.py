from post.models import Post
from post.forms import PostForm
from django.core.urlresolvers import reverse

class PostWriterMixin(object):
  template_name = 'post/edit.html'
  form_class = PostForm

  def get_queryset(self):
    return Post.objects.filter(writer=self.request.user).order_by('-created')

  def form_valid(self, form):
    self.post = form.save(commit=False)
    self.post.writer = self.request.user
    self.post.save()

    return super(PostWriterMixin, self).form_valid(form)

  def get_success_url(self):
    return reverse('posts')
