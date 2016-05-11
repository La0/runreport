from django.views.generic import DetailView, DeleteView
from .mixins import PostWriterMixin, PostMediaMixin
from runreport.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML
from django.http import HttpResponse
from post.models import PostMedia

class PostUploadView(PostWriterMixin, JsonResponseMixin, DetailView):
  json_options = [JSON_OPTION_NO_HTML, ]

  def post(self, request, *args, **kwargs):
    try:
      self.post = self.get_object() # load post first
      self.handle_upload()
      message = 'ok'
      status = 200
    except Exception, e:
      message = 'Fail. %s' % (str(e), )
      status = 500
    return HttpResponse(message, status=status)

  def handle_upload(self):
    # Load uploaded file
    upload = self.request.FILES['file']
    if not upload:
      raise Exception('Missing upload file')

    # Only support image now
    if not upload.content_type.startswith('image/'):
      raise Exception('Only images')

    # Build new media
    media = PostMedia.objects.create(post=self.post, type='image source', size=upload.size)
    media.use_filename(upload.name)
    media.write_upload(upload)
    media.build_thumbnail()
    media.build_crop()

    return media

class PostMediaDeleteView(PostMediaMixin, JsonResponseMixin, DeleteView):
  template_name = 'post/media.delete.html'
