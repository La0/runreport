#!coding=utf-8
from django.db import models
from users.models import Athlete
from coach.mail import MailBuilder
from datetime import datetime
from club import ROLES
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Club(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True, max_length=20)
  members = models.ManyToManyField(Athlete, through='ClubMembership')
  main_trainer = models.ForeignKey(Athlete, null=True, blank=True, related_name="club_main_trainer")
  manager = models.ForeignKey(Athlete, related_name="club_manager")

  # Users limits
  max_staff = models.IntegerField(default=1)
  max_trainer = models.IntegerField(default=2)
  max_athlete = models.IntegerField(default=20)

  # Extra infos
  address = models.CharField(max_length=250)
  zipcode = models.CharField(max_length=10)
  city = models.CharField(max_length=250)

  # Demo dummy club ?
  demo = models.BooleanField(default=False)

  # Private club ?
  private = models.BooleanField(default=False)

  def __unicode__(self):
    return self.name

  def get_private_hash(self):
    '''
    Build a secret hash to join private club
    '''
    from hashlib import md5
    contents = '%s:club:%d' % (settings.SECRET_KEY, self.pk)
    return md5(contents).hexdigest()[0:10]

  def load_stats(self):
    '''
    Count available and used accounts
    '''
    stats = []
    types = ('staff', 'trainer', 'athlete')
    for t in types:
      max = getattr(self, 'max_%s' % t)
      used = self.clubmembership_set.filter(role=t).count()
      stats.append({
        'type' : t,
        'max' : max,
        'used' : used,
        'diff' : max - used,
        'percent' : round(100 * (max - used) / max)
      })
    return stats

  def has_user(self, user):
    return self.clubmembership_set.filter(user=user).count() == 1

class ClubMembership(models.Model):
  user = models.ForeignKey(Athlete, related_name="memberships")
  club = models.ForeignKey(Club)
  trainers = models.ManyToManyField(Athlete, related_name="trainees")
  role = models.CharField(max_length=10, choices=ROLES)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('user', 'club'),)

  def mail_club(self):
    # Send mail to club manager
    # about a new prospect
    context = {
      'manager' : self.club.manager,
      'club' : self.club,
      'user' : self.user,
    }
    mb = MailBuilder('mail/club_prospect.html', self.club.manager.language)
    mb.to = [self.club.manager.email]
    mb.subject = 'Nouvelle inscription au club %s' % (self.club.name, )
    mail = mb.build(context)
    mail.send()

  def mail_user(self, old_role):
    # Send mail to user
    # about a role evolution
    context = {
      'club' : self.club,
      'user' : self.user,
      'old_role' : old_role,
      'new_role' : self.role,
    }
    mb = MailBuilder('mail/user_role.html', self.user.language)
    mb.to = [self.user.email]
    mb.subject = 'Role dans le club %s' % (self.club.name, )
    mail = mb.build(context)
    mail.send()

class ClubLink(models.Model):
  club = models.ForeignKey(Club, related_name="links")
  name = models.CharField(_('Link name'), max_length=250)
  url = models.URLField(_('Link address'), max_length=250)
  position = models.IntegerField()

class ClubInvite(models.Model):
  INVITE_TYPES = (
    ('create', 'Create a club (Beta)'),
  )
  sender = models.ForeignKey(Athlete, related_name="inviter", limit_choices_to={'is_staff':True})
  recipient = models.EmailField()
  name = models.CharField(max_length=250, null=True, blank=True)
  club = models.ForeignKey(Club, null=True, blank=True, related_name="invites")
  type = models.CharField(max_length=15, choices=INVITE_TYPES)
  slug = models.CharField(max_length=30, unique=True, blank=True) # not a slug: no char restriction
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  sent = models.DateTimeField(null=True, blank=True)
  used = models.DateTimeField(null=True, blank=True)

  class Meta:
    unique_together = (('recipient', 'type'),)

  def __unicode__(self):
    return '%s - %s' % (self.recipient, self.slug)

  def save(self, *args, **kwargs):
    if not self.slug:
      self.build_slug()
    super(ClubInvite, self).save(*args, **kwargs)

  def build_slug(self, length=10):
    '''
    Build the slug using random chars & digits
    '''
    import string
    import random
    chars = string.letters + string.digits
    self.slug = ''.join(random.Random().sample(chars, length))

  @models.permalink
  def get_absolute_url(self):
    return ('club-invite', (self.slug, ))

  def warn_sender(self):
    '''
    Send a warning message to sender
    Used when the invite is asked
    '''
    context = {
      'invite' : self,
    }
    mb = MailBuilder('mail/club_invite_asked.html', self.sender.language)
    mb.to = [self.sender.email]
    mb.subject = 'Demande Invitation RunReport.fr'
    mail = mb.build(context)
    mail.send()

  def send(self):
    '''
    Send the invite by mail
    '''
    if self.sent:
      raise Exception('Invite already sent')

    context = {
      'invite_url' : self.get_absolute_url(),
      'name' : self.name,
    }
    mb = MailBuilder('mail/club_invite.html', 'fr') # Default to french
    mb.to = [self.recipient]
    mb.subject = 'Invitation RunReport.fr'
    mail = mb.build(context)
    mail.send()

    # Save sent date
    self.sent = datetime.now()
    self.save()

  def use(self, club):
    '''
    Mark the invite as used
    '''
    # Set used
    self.used = datetime.now()
    self.club = club
    self.save()
