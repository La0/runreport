from django.db import models
from django.contrib.auth.models import User

class Club(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True, max_length=20)
  members = models.ManyToManyField(User, through='ClubMembership')
  main_trainer = models.ForeignKey(User, null=True, blank=True, related_name="club_main_trainer")
  manager = models.ForeignKey(User, related_name="club_manager")

  # Users limits
  max_staff = models.IntegerField(default=1)
  max_trainer = models.IntegerField(default=2)
  max_athlete = models.IntegerField(default=20)

  # Extra infos
  address = models.CharField(max_length=250)
  zipcode = models.CharField(max_length=10)
  city = models.CharField(max_length=250)

  def __unicode__(self):
    return self.name

class ClubMembership(models.Model):
  CLUB_ROLES = (
    ('athlete', 'Athlete'),
    ('trainer', 'Trainer'),
    ('staff', 'Staff'), # For presidents...
    ('archive', 'Archive'),
  )
  user = models.ForeignKey(User, related_name="memberships")
  club = models.ForeignKey(Club)
  trainers = models.ManyToManyField(User, related_name="trainees")
  role = models.CharField(max_length=10, choices=CLUB_ROLES)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('user', 'club'),)

class ClubLink(models.Model):
  club = models.ForeignKey(Club, related_name="links")
  name = models.CharField(max_length=250)
  url = models.URLField(max_length=250)
  position = models.IntegerField()

class ClubInvite(models.Model):
  INVITE_TYPES = (
    ('create', 'Create a club (Beta)'),
    ('trainer', 'Add a trainer'),
    ('athlete', 'Add an athlete'),
  )
  sender = models.ForeignKey(User)
  recipient = models.EmailField(null=True, blank=True)
  club = models.ForeignKey(Club, null=True, blank=True, related_name="invites")
  type = models.CharField(max_length=15, choices=INVITE_TYPES)
  slug = models.CharField(max_length=30, unique=True, blank=True) # not a slug: no char restriction
  private = models.BooleanField(default=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  sent = models.DateTimeField(null=True, blank=True)
  used = models.DateTimeField(null=True, blank=True)

  def save(self, *args, **kwargs):
    if not self.slug:
      self.build_slug()
    super(ClubInvite, self).save(*args, **kwargs)

  def build_slug(self):
    '''
    Build the slug using an hashed part
     only when private
    '''
    self.slug = "%s:%s" % (self.club.slug, self.type)
    if not self.private:
      return self.slug
    from hashlib import md5
    from base64 import b64encode
    h = md5("Coach:%d:%d:%s" % (self.club.pk, self.sender.pk, self.type)).digest()
    h = b64encode(h)
    self.slug += ":%s" % (h[0:8],)
    return self.slug

  def apply(self, user):
    '''
    Apply the invite to this user
    '''
    if self.type not in ('trainer', 'athlete'):
      raise Exception("Invalid type to apply: %s" % self.type)

    if self.private:
      # Directly apply private 
      cm, _ = ClubMembership.objects.get_or_create(club=self.club, user=user)
      cm.role = self.type
      cm.save()
    else:
      # TODO: only support athlete here
      # TODO: check stats before applying
      # TODO: when there is no room, set as propect
      pass

    # Set used
    from datetime import datetime
    self.used = datetime.now()
    self.save()
