from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
  # Link to user
  user = models.OneToOneField(User)

  # Trainer
  trainer = models.ForeignKey(User, null=True, related_name='trainee')

  # Personal infos for trainer
  birthday = models.DateField(null=True, blank=True)
  vma = models.FloatField(null=True, blank=True)
  frequency = models.IntegerField(null=True, blank=True)
  height = models.IntegerField(null=True, blank=True)
  weight = models.IntegerField(null=True, blank=True)

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
  '''
  if created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
