from post.models import Post, PostMedia
from post.forms import PostForm
from django.urls import reverse


class PostWriterMixin(object):
    form_class = PostForm
    template_name = 'post/edit.html'

    def get_queryset(self):
        return Post.objects.filter(
            writer=self.request.user).order_by('-created')

    def form_valid(self, form):
        self.post = form.save(commit=False)
        self.post.writer = self.request.user
        self.post.save()

        return super(PostWriterMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('post-edit', args=(self.post.slug, ))

    def get_context_data(self, *args, **kwargs):
        context = super(
            PostWriterMixin,
            self).get_context_data(
            *
            args,
            **kwargs)

        # Add crops
        if hasattr(self, 'object') and hasattr(self.object, 'medias'):
            context['images'] = self.object.medias.filter(
                type='image crop').prefetch_related('parent')

        return context


class PostMediaMixin(object):
    context_object_name = 'media'

    def get_queryset(self):
        # Limit to owned medias
        return PostMedia.objects.filter(post__writer=self.request.user)

    def get_success_url(self):
        return reverse('post-edit', args=(self.object.post.slug, ))
