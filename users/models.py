# coding=utf-8
import glob
import os
import math
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.core import validators
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from hashlib import md5
from datetime import datetime
from PIL import Image
from avatar_generator import Avatar

PRIVACY_LEVELS = (
  ('public', u'Public'),
  ('club', u'Club'),
  ('private', u'Privé'),
)

class AthleteBase(AbstractBaseUser, PermissionsMixin):
  '''
  Straight from AbstractUser
  except for the unicity of email
  '''
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']

  username = models.CharField(_('username'), max_length=30, unique=True,
    help_text=_('Required. 30 characters or fewer. Letters, digits and '
    '@/./+/-/_ only.'),
    validators=[
      validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
    ])
  first_name = models.CharField(_('first name'), max_length=30, blank=True)
  last_name = models.CharField(_('last name'), max_length=30, blank=True)
  email = models.EmailField(_('email address'), blank=True, unique=True)
  is_staff = models.BooleanField(_('staff status'), default=False,
    help_text=_('Designates whether the user can log into this admin '
    'site.'))
  is_active = models.BooleanField(_('active'), default=True,
    help_text=_('Designates whether this user should be treated as '
    'active. Unselect this instead of deleting accounts.'))
  date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

  objects = UserManager()

  def get_username(self):
    # Still use username, instead of email
    return self.username

  def get_short_name(self):
    return self.first_name or self.username

  class Meta:
    verbose_name = _('user')
    verbose_name_plural = _('users')
    abstract = True

# Alias accessible from model field
def build_avatar_path(instance, filename):
  return instance.build_avatar_path()

class Athlete(AthleteBase):
  # Personal infos for trainer
  birthday = models.DateField(null=True, blank=True)
  category = models.ForeignKey('UserCategory', null=True, blank=True)
  vma = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
  frequency = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
  frequency_rest = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
  height = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
  weight = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
  comment = models.TextField(null=True, blank=True)
  nb_sessions = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
  license = models.CharField(max_length=12, null=True, blank=True)

  # Sport
  default_sport = models.ForeignKey('sport.Sport', default=3, limit_choices_to={'depth': 1,}) # default to running

  # Mail
  auto_send = models.BooleanField(default=False)

  # Garmin
  garmin_login = models.CharField(max_length=255, null=True, blank=True)
  garmin_password = models.TextField(null=True, blank=True)

  # Demo dummy account ?
  demo = models.BooleanField(default=False)

  # Avatar image
  avatar = models.ImageField(upload_to=build_avatar_path)

  # Profile privacy
  privacy_profile = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='club')
  privacy_avatar = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='club')
  privacy_races = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='club')
  privacy_records = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='club')
  privacy_stats = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='club')
  privacy_calendar = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='private')
  privacy_comments = models.CharField(max_length=50, choices=PRIVACY_LEVELS, default='club')

  def search_category(self):
    if not self.birthday:
      return None
    try:
      self.category = UserCategory.objects.get(min_year__gte=self.birthday.year, max_year__lte=self.birthday.year)
    except:
      self.category = None
      pass
    return self.category

  def clean_avatars(self):
    # Remove previous avatars for this user
    avatar_filter = os.path.join(settings.MEDIA_ROOT, 'avatars', '%s.*' % self.username)
    for f in glob.glob(avatar_filter):
      os.unlink(f)

  def build_avatar_path(self):
    # Build an avatar file path for a user
    # using his username, and a secret hash
    # unique per upload
    h = md5('%s:%s:%d' % (settings.SECRET_KEY, datetime.now(), self.pk)).hexdigest()
    return 'avatars/%s.%s.png' % (self.username, h[0:8])


  def build_avatar(self, size=400):
    path = self.build_avatar_path()
    full_path = os.path.join(settings.MEDIA_ROOT, path)

    # Build a random default avatar
    avatar_data = Avatar.generate(size, self.first_name)
    with open(full_path, 'w+') as fd:
      fd.write(avatar_data)

    # Save the new path, but don't save
    self.avatar = path

    return path

  def crop_avatar(self, crop_size=400):
    # Crop the recently uploaded avatar
    if not os.path.exists(self.avatar.path):
      raise Exception('Missing avatar file :%s' % self.avatar.file)

    # Load image
    img = Image.open(self.avatar.file)
    w,h = img.size
    small_size = min(w,h)

    # Resize before crop ?
    if small_size > crop_size:
      ratio = float(crop_size) / float(small_size)
      w = int(math.floor(w * ratio))
      h = int(math.floor(h * ratio))
      img = img.resize((w, h))

    crop_box = None
    if w < h:
      # Vertical Crop
      offset = int(math.floor((h - crop_size) / 2))
      crop_box = (0, offset, w, h - offset)
    elif w > h:
      # Horizontal crop
      offset = int(math.floor((w - crop_size) / 2))
      crop_box = (offset, 0, w - offset, h)

    # Do the crop
    if crop_box:
      img = img.crop(crop_box)

    # Save the resulting image
    img.save(self.avatar.path, 'png')

  def is_trainer(self, athlete):
    '''
    Simple check to see if this user
    is the trainer of an athlete
    '''
    for m in athlete.memberships.all():
      if self in m.trainers.all():
        return True
    return False

  def get_visitor_rights(self, visitor):
    '''
    Load the visitor rights for connected visitor
    for this current user
    '''

    # All rights when visitor is member
    if visitor == self:
      return ('public', 'club', 'private')

    # Club & public rights
    # when visitor is in same club
    # with an active profile
    if visitor.is_authenticated():
      member_clubs = set([m['club__id'] for m in self.memberships.exclude(role__in=('prospect', 'archive')).values('club__id')])
      user_clubs = set([m['club__id'] for m in visitor.memberships.exclude(role__in=('prospect', 'archive')).values('club__id')])
      if len(member_clubs & user_clubs) > 0:
        return ('public', 'club')

    # By default, public
    return ('public', )

  def get_privacy_rights(self, visitor):
    '''
    Load privacy rights for a visitor toward this user
    '''
    privacy = []
    fields = [k[8:] for k in dir(self) if k.startswith('privacy')] # all the current privacy fields

    # Super user views everything
    if visitor.is_superuser:
      privacy = fields # all access
      privacy += ['admin', ] # and has admin right
      return privacy

    # A trainer sees evertything for his athletes
    # The club manager see every athletes
    trainers_roles = ['athlete', 'staff', 'trainer']
    for m in self.memberships.all():
      is_manager = m.club.manager == visitor
      if visitor in m.trainers.all() or is_manager:
        # Add archive roles for managers
        trainers_roles += is_manager and ['archive', ] or []
        if m.role in trainers_roles:
          privacy = fields # all access
          privacy += ['trainer', ] # and has trainer right
          return privacy

    # Load all member privacy settings
    rights = self.get_visitor_rights(visitor)
    privacy = [f for f in fields if getattr(self, 'privacy_%s' % f) in rights]

    return privacy

class UserCategory(models.Model):
  code = models.CharField(max_length=10)
  name = models.CharField(max_length=120)
  min_year = models.IntegerField()
  max_year = models.IntegerField()

  def __unicode__(self):
    return u'%s %s ' % (self.code, self.name)
