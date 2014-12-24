from django.db import models
from django.utils.translation import ugettext_lazy as _

POST_TYPES = (
  ('race', _('Race')),
  ('training', _('Training')),
  ('blog', _('Blog')),
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
  sessions = models.ManyToManyField('sport.SportSession', related_name='posts')

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # Simple incremental revision on edits
  revision = models.IntegerField(default=1)

  class Meta:
    unique_together = (('writer', 'slug'), )

  def __unicode__(self):
    return self.title
