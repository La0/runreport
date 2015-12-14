# coding=utf-8
from django.db import models
from . import SESSION_TYPES
from django.utils.translation import ugettext_lazy as _
import vinaigrette
from messages.models import Conversation
from ..tasks import sync_session_gcal
import markdown

class Sport(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True)
  parent = models.ForeignKey('Sport', null=True)
  depth = models.IntegerField(default=0)

  strava_name = models.CharField(max_length=250, null=True, blank=True)

  class Meta:
    db_table = 'sport_list'
    app_label = 'sport'

  def __unicode__(self):
    return self.name

  def get_parent(self):
    # Always give a valid parent
    if self.depth <= 1 or not self.parent:
      return self
    return self.parent

  def get_category(self):
    # Always give a valid parent category
    return self.get_parent().slug

  @property
  def icon(self):
    return 'icon-sport-%s' % self.slug

# i18n
vinaigrette.register(Sport, ['name', ])

class SportSession(models.Model):
  day = models.ForeignKey('SportDay', related_name="sessions")
  sport = models.ForeignKey(Sport)
  name = models.CharField(max_length=255, null=True, blank=True)
  comment = models.TextField(_('session comment'), null=True, blank=True)
  comment_html = models.TextField(null=True, blank=True) # generated from potential markdown source above
  type = models.CharField(max_length=12, default='training', choices=SESSION_TYPES)
  race_category = models.ForeignKey('RaceCategory', verbose_name=_('Race category'), null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  note = models.IntegerField(null=True, blank=True)

  # Performances
  time = models.DurationField(null=True, blank=True, verbose_name=_('Time'))
  distance = models.FloatField(null=True, blank=True, verbose_name=_('Distance'))
  elevation_gain = models.FloatField(null=True, blank=True, verbose_name=_('Elevation gain'))
  elevation_loss = models.FloatField(null=True, blank=True, verbose_name=_('Elevation loss'))

  # Google Calendar
  gcal_id = models.CharField(max_length=255, null=True, blank=True)

  # Comments
  comments_public = models.OneToOneField('messages.Conversation', null=True, blank=True, related_name='session_public')
  comments_private = models.OneToOneField('messages.Conversation', null=True, blank=True, related_name='session_private')

  # Gear items
  gear = models.ManyToManyField('gear.GearItem', related_name='sessions')

  class Meta:
    db_table = 'sport_session'
    app_label = 'sport'

  def save(self, *args, **kwargs):
    created = self.pk is None

    # No race category when we are not in race
    if self.type != 'race':
      self.race_category = None

    # Only allow depth 1 sports
    if self.sport.depth != 1:
      raise Exception("Invalid sport '%s', only level 1 authorized for SportSession" % self.sport)

    # Try to render html version of comment
    if self.comment:
        self.comment_html = markdown.markdown(self.comment)

    super(SportSession, self).save(*args, **kwargs)

    # Sync event in Google Calendar
    if self.gcal_id or self.day.week.user.has_gcal:
      sync_session_gcal.delay(self)

    # Add default gear per sport
    if created and not self.gear.exists():
      try:
        self.gear = self.day.week.user.items.filter(sports=self.sport)
      except Exception, e:
        print 'Failed to apply default gear', e


  def delete(self, *args, **kwargs):

    # Delete event in Google Calendar
    if self.gcal_id:
      sync_session_gcal.delay(self, delete=True)

    super(SportSession, self).delete(*args, **kwargs)


  def build_conversation(self, type):
    '''
    Init a conversation private|public
    '''
    if type not in ('public', 'private'):
      raise Exception('Invalid conversation name')

    name = 'comments_%s' % type
    if getattr(self, name, None):
      raise Exception('Conversation already exists')

    conversation = Conversation.objects.create(type=name, session_user=self.day.week.user)
    setattr(self, name, conversation)
    self.save()

    return conversation
