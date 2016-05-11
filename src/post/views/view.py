from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from post.models import Post

class PostView(DetailView):
  template_name = 'post/view.html'

  def get_object(self):
    '''
    Load user's post, allow writer to view its draft
    '''
    post = get_object_or_404(Post, writer__username=self.kwargs['username'], slug=self.kwargs['slug'])
    if not post.published and self.request.user != post.writer:
      raise Http404()

    return post

  def get_context_data(self, *args, **kwargs):
    context = super(PostView, self).get_context_data(*args, **kwargs)

    # Embed Medias
    context['medias'] = self.object.medias.filter(type='image crop').prefetch_related('parent', 'post')

    # Embed sessions
    context['sessions'] = self.object.sessions.all().order_by('day__date').prefetch_related('track', 'sport', 'day')

    return context
