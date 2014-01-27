from django.db import models
from users.models import Athlete
from helpers import nameize
from markdown import markdown

PAGE_TYPES = (
  ('help', 'Help'),
  ('news', 'News'),
)

class Page(models.Model):
  slug = models.SlugField(blank=True)
  name = models.CharField(max_length=255)
  markdown = models.TextField(null=True, blank=True)
  html = models.TextField(null=True, blank=True)
  type = models.CharField(max_length=12, choices=PAGE_TYPES)
  user = models.ForeignKey(Athlete)
  published = models.BooleanField()
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('slug', 'type'))

  @models.permalink
  def get_absolute_url(self):
    return ('page', (self.type, self.slug))

  def save(self, *args, **kwargs):
    # Init slug
    if self.slug == '':
      self.slug = nameize(self.name)

    # Generate html
    self.html = markdown(self.markdown)

    super(Page, self).save(*args, **kwargs)
