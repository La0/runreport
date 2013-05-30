# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
  # Link to user
  user = models.OneToOneField(User)

  # Personal infos for trainer
  birthday = models.DateField(null=True, blank=True)
  vma = models.FloatField(null=True, blank=True)
  frequency = models.IntegerField(null=True, blank=True)
  frequency_rest = models.IntegerField(null=True, blank=True)
  height = models.IntegerField(null=True, blank=True)
  weight = models.IntegerField(null=True, blank=True)
  comment = models.TextField(null=True, blank=True)
  nb_sessions = models.IntegerField(null=True, blank=True)
  license = models.CharField(max_length=12, null=True, blank=True)

  # Mail
  auto_send = models.BooleanField(default=False)

  # Garmin
  garmin_login = models.CharField(max_length=255, null=True, blank=True)
  garmin_password = models.TextField(null=True, blank=True)

  # Reminders
  reminder_monday   = models.TimeField(null=True, blank=True)
  reminder_tuesday  = models.TimeField(null=True, blank=True)
  reminder_wednesday = models.TimeField(null=True, blank=True)
  reminder_thursday = models.TimeField(null=True, blank=True)
  reminder_friday   = models.TimeField(null=True, blank=True)
  reminder_saturday = models.TimeField(null=True, blank=True)
  reminder_sunday   = models.TimeField(null=True, blank=True)

def create_user_profile(sender, instance, created, **kwargs):
  '''
  Create a profile on user save()
  Behave well when using fab syncdb
  '''
  if (kwargs.get('created', True) and not kwargs.get('raw', False)) and created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
