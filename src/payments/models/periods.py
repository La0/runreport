# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from payments.tasks import notify_admin, notify_club
import logging

logger = logging.getLogger('payments')

PERIOD_STATUS = (
  ('active', _('Active')),
  ('paid', _('Paid')),
  ('expired', _('Expired')),
  ('error', _('Error')),
)

# Pricing Levels
LEVEL_FREE = 'free'
LEVEL_PREMIUM_S = 'premium_s'
LEVEL_PREMIUM_M = 'premium_m'
LEVEL_PREMIUM_L = 'premium_l'
PERIOD_LEVELS = (
    (LEVEL_FREE, 'Free'),
    (LEVEL_PREMIUM_S, u'Premium Small - 9,90€'),
    (LEVEL_PREMIUM_M, u'Premium Medium - 19,90€'),
    (LEVEL_PREMIUM_L, u'Premium Large - 49,90€'),
)
LEVEL_PRICES = {
    LEVEL_FREE : 0.00,
    LEVEL_PREMIUM_S : 9.90,
    LEVEL_PREMIUM_M : 19.90,
    LEVEL_PREMIUM_L : 49.90,
}


class PaymentPeriod(models.Model):
  '''
  A subscription between a club and an offer
  '''
  # Link to clubs
  club = models.ForeignKey('club.Club', related_name='periods')

  # Max active roles
  nb_athletes = models.IntegerField(default=0)
  nb_trainers = models.IntegerField(default=0)
  nb_staff = models.IntegerField(default=0)

  # Status
  status = models.CharField(choices=PERIOD_STATUS, max_length=20, default='active')

  # Mangopay Id transaction
  mangopay_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
  level = models.CharField(max_length=20, choices=PERIOD_LEVELS, default=LEVEL_FREE)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  start = models.DateTimeField()
  end = models.DateTimeField()

  def __unicode__(self):
      return u'{} from {} to {} : {}'.format(self.club.name, self.start.date(), self.end.date(), self.level)

  @property
  def remaining_days(self):
    '''
    Calc remaining days in subscription
    until end
    '''
    diff = self.end - timezone.now()
    return diff.days

  @property
  def is_free(self):
    return self.level == LEVEL_FREE

  @property
  def is_premium(self):
    return self.level in (LEVEL_PREMIUM_S, LEVEL_PREMIUM_M, LEVEL_PREMIUM_L)

  def update_roles_count(self):
    """
    Update all the roles count from club
    """
    # Calc all current roles nb
    counts = self.club.clubmembership_set.values('role').annotate(nb=models.Count('role'))
    roles = dict([(c['role'], c['nb']) for c in counts])

    # Only keep max value for each role
    self.nb_trainers = max(self.nb_trainers, roles.get('trainer', 0))
    self.nb_athletes = max(self.nb_athletes, roles.get('athlete', 0))
    self.nb_staff = max(self.nb_staff, roles.get('staff', 0))

  def detect_level(self):
    '''
    Detect payment level according to user nb
    '''
    if self.nb_trainers <= 1 and self.nb_athletes <= 10:
        self.level = LEVEL_FREE

    elif self.nb_trainers <= 3 and self.nb_athletes <= 30:
        self.level = LEVEL_PREMIUM_S

    elif self.nb_trainers <= 10 and self.nb_athletes <= 100:
        self.level = LEVEL_PREMIUM_M

    else:
        self.level = LEVEL_PREMIUM_L

    return self.level

  @property
  def amount(self):
    """
    Gives amount to pay according to level
    """
    return LEVEL_PRICES[self.level]


  def pay(self):
    '''
    Pay the subscription, automatically from task
    '''

    # Create payment on MangoPay
    try:
      if not self.club.has_valid_card:
        raise Exception('Missing valid card')

      logger.info('Create payment for %s (%f euros) - sub #%d' % (self.club, self.amount, self.pk))
      resp = self.club.init_payment(self.amount)

      if resp.Status == 'SUCCEEDED':
        # Update status
        self.status = 'paid'

        # End current period
        now = timezone.now()
        self.end = now

        # Create new current period
        end = now + timedelta(days=settings.PAYMENTS_PERIOD)
        PaymentPeriod.objects.create(club=self.club, start=now, end=end)

        # Send success mails
        notify_club.delay(self)
      else:
        raise Exception('Invalid response from Mangopay %s' % resp.Status)
    except Exception, e:
      logger.error('Payment failed for club %s : %s' % (self.club, e))

      # Update status
      self.status = 'error'

      # Send manual payment mail
      notify_club.delay(self)


    # Save new status
    self.save()

    # Send admin email
    notify_admin.delay(self)
