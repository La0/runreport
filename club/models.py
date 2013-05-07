from django.db import models
from django.contrib.auth.models import User

class Club(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True)
  members = models.ManyToManyField(User, through='ClubMembership')
  main_trainer = models.ForeignKey(User, null=True, blank=True, related_name="club_main_trainer")

  def __unicode__(self):
    return self.name

class ClubMembership(models.Model):
  CLUB_ROLES = (
    ('athlete', 'Athlete'),
    ('trainer', 'Trainer'),
  )
  user = models.ForeignKey(User)
  club = models.ForeignKey(Club)
  role = models.CharField(max_length=10, choices=CLUB_ROLES)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('user', 'club'),)
