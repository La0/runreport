from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from hashlib import md5
import os
import re
from helpers import crop_image
from PIL import Image
from messages.models import Conversation, TYPE_POST

POST_TYPES = (
    ('race', _('Race')),
    ('training', _('Training')),
    ('blog', _('Blog')),
)

POST_MEDIAS = (
    ('image source', _('Source Image')),
    ('image thumb', _('Thumbnail Image')),
    ('image crop', _('Cropped Image')),
)


class Post(models.Model):
    writer = models.ForeignKey('users.Athlete', related_name='posts')
    slug = models.SlugField(_('Name in the url'))
    published = models.BooleanField(default=False)
    type = models.CharField(_('Post Type'), max_length=15, choices=POST_TYPES)

    # Content
    title = models.CharField(_('Post title'), max_length=255)
    html = models.TextField(_('Post content'))

    # Attached sessions
    sessions = models.ManyToManyField(
        'sport.SportSession', related_name='posts')

    # Comments
    conversation = models.OneToOneField(
        'messages.Conversation',
        null=True,
        blank=True,
        related_name='post')

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Simple incremental revision on edits
    revision = models.IntegerField(default=1)

    class Meta:
        unique_together = (('writer', 'slug'), )

    def __str__(self):
        return self.title

    def add_comment(self, message, writer):
        '''
        Add a new comment to the conversation
        Init the conversation if needed
        '''

        # Create a new conversation
        if not self.conversation:
            self.conversation = Conversation.objects.create(type=TYPE_POST)
            self.save()

        # Save a new message for user
        message = self.conversation.messages.create(
            writer=writer, message=message)

        # Add notifications
        self.conversation.notify(message)

        return message


class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name='medias')
    parent = models.ForeignKey(
        'post.PostMedia',
        related_name='children',
        null=True)
    type = models.CharField(max_length=25, choices=POST_MEDIAS)

    # Metadata
    name = models.CharField(max_length=255, null=True, blank=True)
    size = models.IntegerField()  # in bytes
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def fullname(self):
        if self.name:
            return self.name
        if self.parent:
            return self.parent.fullname
        return None

    @property
    def path(self):
        return self.build_path(absolute=True)

    @property
    def url(self):
        return os.path.join(settings.MEDIA_URL,
                            self.build_path(absolute=False))

    def build_path(self, absolute=False):
        '''
        Generate a path for current media
        '''
        name_contents = '%s:%d:%d' % (
            settings.SECRET_KEY, self.post_id, self.pk)
        ext = 'jpg'  # only image for the moment
        name = '%s.%s' % (md5(name_contents).hexdigest(), ext)
        path = absolute and settings.MEDIA_ROOT or ''
        path = os.path.join(path, 'posts', str(self.post_id), name)

        return path

    def delete(self):
        '''
        Delete all children and cleanup files
        '''
        # Cleanup
        if os.path.exists(self.path):
            os.remove(self.path)

        # Delete all children
        for c in self.children.all():
            c.delete()

        # Base deletion
        super(PostMedia, self).delete()

    def use_filename(self, filename):
        '''
        Use filename to build clean name
        '''

        # Remove extension
        if '.' in filename:
            filename = filename[:filename.rindex('.')]

        # Replace special chars by spaces
        regex = r'([\-_\+\.]+)'
        filename = re.sub(regex, ' ', filename)

        # Use cleaned filename as name
        self.name = filename
        self.save()

    def write_upload(self, upload):
        '''
        Write an uploaded file on path
        '''
        post_dir = os.path.dirname(self.path)
        if not os.path.exists(post_dir):
            os.makedirs(post_dir)

        with open(self.path, 'wb+') as fd:
            for chunk in upload.chunks():
                fd.write(chunk)

    def build_thumbnail(self, size=(300, 300)):
        '''
        For images, build thumbnail
        '''
        src = Image.open(self.path)

        # Build thumbnail
        src.thumbnail(size)

        # Save in new media
        w, h = src.size
        media = PostMedia.objects.create(
            post=self.post,
            type='image thumb',
            parent=self,
            width=w,
            height=h,
            size=0)
        src.save(media.path, 'JPEG')

        # Pillow does not provide file size :(
        media.size = os.stat(media.path).st_size
        media.save()

        return media

    def build_crop(self, size=400):
        '''
        For images, build crop
        '''

        # Create new media
        media = PostMedia.objects.create(
            post=self.post,
            type='image crop',
            parent=self,
            width=size,
            height=size,
            size=0)

        # Crop image
        crop_image(self.path, media.path, size)

        # Pillow does not provide file size :(
        media.size = os.stat(media.path).st_size
        media.save()

        return media
