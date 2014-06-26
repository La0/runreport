# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.core import validators
from django.utils import timezone

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

class Athlete(AthleteBase):
  # Personal infos for trainer
  birthday = models.DateField(null=True, blank=True)
  category = models.ForeignKey('UserCategory', null=True, blank=True)
  vma = models.FloatField(null=True, blank=True)
  frequency = models.IntegerField(null=True, blank=True)
  frequency_rest = models.IntegerField(null=True, blank=True)
  height = models.IntegerField(null=True, blank=True)
  weight = models.IntegerField(null=True, blank=True)
  comment = models.TextField(null=True, blank=True)
  nb_sessions = models.IntegerField(null=True, blank=True)
  license = models.CharField(max_length=12, null=True, blank=True)

  # Sport
  default_sport = models.ForeignKey('sport.Sport', default=3, limit_choices_to={'depth': 1,}) # default to running

  # Mail
  auto_send = models.BooleanField(default=False)

  # Garmin
  garmin_login = models.CharField(max_length=255, null=True, blank=True)
  garmin_password = models.TextField(null=True, blank=True)

  def search_category(self):
    if not self.birthday:
      return None
    try:
      self.category = UserCategory.objects.get(min_year__gte=self.birthday.year, max_year__lte=self.birthday.year)
    except:
      self.category = None
      pass
    return self.category

class UserCategory(models.Model):
  code = models.CharField(max_length=10)
  name = models.CharField(max_length=120)
  min_year = models.IntegerField()
  max_year = models.IntegerField()

  def __unicode__(self):
    return u'%s %s ' % (self.code, self.name)
