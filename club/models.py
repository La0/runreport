#!coding=utf-8
from django.db import models
from users.models import Athlete
from runreport.mail import MailBuilder
from runreport.mailman import MailMan
from datetime import datetime
from club import ROLES
from club.tasks import sync_mailing_membership
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from payments import get_api
from mangopaysdk.entities.userlegal import UserLegal
from mangopaysdk.entities.wallet import Wallet
from mangopaysdk.types.address import Address
from django_countries.fields import CountryField
import time

class Club(models.Model):
  name = models.CharField(_('Club name'), max_length=250)
  slug = models.SlugField(_('Slug'), help_text="Represents the club's name in urls", unique=True, max_length=20)
  members = models.ManyToManyField(Athlete, through='ClubMembership')
  main_trainer = models.ForeignKey(Athlete, null=True, blank=True, related_name="club_main_trainer")
  manager = models.ForeignKey(Athlete, related_name="club_manager")

  # Users limits
  max_staff = models.IntegerField(default=1)
  max_trainer = models.IntegerField(default=1)
  max_athlete = models.IntegerField(default=10)

  # Extra infos
  address = models.CharField(_('Address'), max_length=250)
  zipcode = models.CharField(_('Zip code'), max_length=10)
  city = models.CharField(_('City'), max_length=250)
  country = CountryField(default='FR', verbose_name=_('Country'))

  # Payment
  mangopay_id = models.CharField(max_length=50, null=True, blank=True)
  wallet_id = models.CharField(max_length=50, null=True, blank=True)

  # Demo dummy club ?
  demo = models.BooleanField(default=False)

  # Private club ?
  private = models.BooleanField(_('Private club'), help_text=_('When private, a club is only accessible y its members'), default=False)

  # Mailing list (does not change)
  mailing_list = models.CharField(max_length=255, null=True, blank=True)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

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

  def load_usage_stats(self):
    '''
    Calc usage statistics for this club
    '''

    # Nb of plans by trainers of this club
    from plan.models import Plan, PlanApplied
    from sport.models import SportSession
    plans = Plan.objects.filter(creator__memberships__club=self, creator__memberships__role='trainer').count()

    # Nb of plan applied for athletes
    applied = PlanApplied.objects.filter(user__memberships__club=self, user__memberships__role='athlete').count()

    # Nb of sessions
    sessions = SportSession.objects.filter(day__week__user__memberships__club=self).count()

    return {
      'plans' : plans,
      'plans_applied' : applied,
      'sessions' : sessions,

      # Base roles nb
      'athletes' : self.clubmembership_set.filter(role='athlete').count(),
      'trainers' : self.clubmembership_set.filter(role='trainer').count(),
    }

  def has_user(self, user):
    return self.clubmembership_set.filter(user=user).count() == 1

  @property
  def mailing_list_fqdn(self):
    if not self.mailing_list:
      return None
    return '%s@%s' % (self.mailing_list, settings.MAILMAN_DOMAIN)

  def create_mailing_list(self):
    '''
    Create a mailing list for the club group
    '''
    if self.mailing_list:
      raise Exception('Already a registered mailing list')

    # Create on mailman
    name = self.slug.lower()
    try:
      mm = MailMan()
      mm.create_list(name, self.name)
    except Exception, e:
      print 'Failed to create mailing list %s : %s' % (name, str(e))
      return False

    # Save reference
    self.mailing_list = name
    self.save()

    # Add manager in mailing list
    self.manager.subscribe_mailing(self.mailing_list)

    return True

  def _is_premium(self):
    # helper to check if a user is premium
    return self.subscriptions.filter(offer__target='club', status__in=('active', 'created')).exists()

  # Django disallows direct property
  # use in list displays
  # Cf https://stackoverflow.com/questions/12842095/how-to-display-a-boolean-property-in-the-django-admin
  _is_premium.boolean = True # for admin display

  @cached_property
  def is_premium(self):
    return self._is_premium()

  def sync_mangopay(self):
    '''
    Create user & wallet on mangopay
    '''

    if self.mangopay_id and self.wallet_id:
      raise Exception('Mangopay account & wallet exist')

    # Sync Mangopay account
    if not self.mangopay_id:
      # Build address
      address = Address()
      address.AddressLine1 = self.address
      address.City = self.city
      address.Country = self.country.code
      address.PostalCode = self.zipcode

      # Build legal user
      rr_user = UserLegal()
      rr_user.Name = self.name
      rr_user.LegalPersonType = 'ORGANIZATION' # Support ORGANIZATION ?
      rr_user.LegalRepresentativeFirstName = self.manager.first_name
      rr_user.LegalRepresentativeLastName = self.manager.last_name
      rr_user.LegalRepresentativeAddress = address
      rr_user.LegalRepresentativeEmail = self.manager.email
      bday = self.manager.birthday
      rr_user.LegalRepresentativeBirthday = int(time.mktime((bday.year, bday.month, bday.day, 0, 0, 0, -1, -1, -1)))
      rr_user.LegalRepresentativeNationality = self.manager.nationality.code
      rr_user.LegalRepresentativeCountryOfResidence = self.manager.country.code
      rr_user.Email = self.manager.email

      # Finally create the user
      api = get_api()
      u = api.users.Create(rr_user)
      self.mangopay_id = u.Id

    # Sync Mangopay wallet
    if not self.wallet_id:
      wallet = Wallet()
      wallet.Owners = [self.mangopay_id, ]
      wallet.Description = 'Club %s wallet' % (self.name, )
      wallet.Currency = 'EUR' # always in euros

      # Create the wallet
      api = get_api()
      w = api.wallets.Create(wallet)
      self.wallet_id = w.Id

    # Save changes
    self.save()


class ClubMembership(models.Model):
  user = models.ForeignKey(Athlete, related_name="memberships")
  club = models.ForeignKey(Club)
  trainers = models.ManyToManyField(Athlete, related_name="trainees")
  role = models.CharField(max_length=10, choices=ROLES)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('user', 'club'),)

  def save(self, *args, **kwargs):
    '''
    Sync mailing list on save
    '''
    out = super(ClubMembership, self).save(*args, **kwargs)

    if self.role == 'archive':
      # Remove from mailings
      sync_mailing_membership.delay(self, False)

    elif self.role != 'prospect':
      # Add to mailings
      sync_mailing_membership.delay(self, True)

    return out

  def delete(self, *args, **kwargs):
    '''
    Remove from mailing lists on delete
    '''
    sync_mailing_membership.delay(self, False)

    return super(ClubMembership, self).delete(*args, **kwargs)

  @property
  def groups_owned(self):
    # Helper for api
    return self.user.groups_owned.filter(club=self.club)

  @property
  def athletes(self):
    # Helper for api
    athletes = self.club.clubmembership_set.filter(**{
      'role__in' : ('athlete', 'trainer'),
      'trainers' : self.user,
    })
    athletes = athletes.prefetch_related('user', 'groups')
    athletes = athletes.order_by('user__first_name', 'user__last_name')
    return athletes

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
    ('join', 'Join a club'),
  )
  sender = models.ForeignKey(Athlete, related_name="inviter", limit_choices_to={'is_staff':True})
  recipient = models.EmailField()
  user = models.ForeignKey('users.Athlete', null=True, blank=True) # a recipient user can already exist
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
    mb.to = [self.sender.email, ]
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
      'club' : self.club,
      'user' : self.user,
    }
    templates = {
      'create' : 'mail/club_invite.html',
      'join' : 'mail/subscription.html',
    }
    lang = self.user and self.user.language or 'fr' # Default to french
    mb = MailBuilder(templates[self.type], lang)
    mb.to = [self.recipient, ]
    mb.subject = _('RunReport Invite')
    mail = mb.build(context)
    mail.send()

    # Save sent date
    self.sent = datetime.now()
    self.save()

  def use(self, club=None):
    '''
    Mark the invite as used
    '''
    # Set used
    self.used = datetime.now()
    if club:
      self.club = club
    self.save()

class ClubGroup(models.Model):
  '''
  Group club members for easier plan usage
  '''
  club = models.ForeignKey(Club, related_name='groups')
  name = models.CharField(_('Group name'), max_length=255)
  slug = models.SlugField(_('Name in the url'))
  description = models.TextField(_('Description'), null=True, blank=True)

  # Users
  creator = models.ForeignKey(Athlete, related_name='groups_owned')
  members = models.ManyToManyField(ClubMembership, related_name='groups')

  # Mailing list (does not change)
  mailing_list = models.CharField(max_length=255, null=True, blank=True)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('club', 'slug'), )

  def __unicode__(self):
    return '%s : %s' % (self.club.name, self.name)

  def get_members(self):
    return self.members.all().order_by('user__first_name', 'user__last_name').prefetch_related('user')

  @property
  def nb_members(self):
    # Helper for api
    return self.members.count()

  @property
  def mailing_list_fqdn(self):
    if not self.mailing_list:
      return None
    return '%s@%s' % (self.mailing_list, settings.MAILMAN_DOMAIN)

  def create_mailing_list(self):
    '''
    Create a mailing list for the club group
    '''
    if self.mailing_list:
      raise Exception('Already a registered mailing list')

    # Create on mailman
    name = '%s.%s' % (self.slug, self.club.slug)
    name = name.lower()
    try:
      mm = MailMan()
      mm.create_list(name, self.name)
    except Exception, e:
      print 'Failed to create mailing list %s : %s' % (name, str(e))
      return False

    # Save reference
    self.mailing_list = name
    self.save()

    # Add creator to mailing list
    self.creator.subscribe_mailing(self.mailing_list)

    return True

  def delete_mailing_list(self):
    '''
    Delete a mailing list for the club group
    '''
    if not self.mailing_list:
      raise Exception('Missing a mailing list')

    try:
      mm = MailMan()
      mm.delete_list(self.mailing_list)
    except Exception, e:
      print 'Failed to delete mailing list %s : %s' % (self.mailing_list, str(e))
      return False

    # Kill reference
    # No save here, it kills the delete from task
    self.mailing_list = None

    return True
