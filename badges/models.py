from django.db import models
from django.utils import timezone
from django.db.utils import IntegrityError

class BadgeCategory(models.Model):
  '''
  Group badges by categories
  '''
  name = models.CharField(max_length=250, unique=True)

  def __unicode__(self):
    return self.name

  def get_user_value(self, user):
    '''
    Get the user value for each category
    '''
    from sport.models import SportSession
    sessions = SportSession.objects.filter(day__week__user=user)

    if self.name == 'distance':
      # Sum of distance for user
      agg = sessions.aggregate(total=models.Sum('distance'))
      return agg['total']

    if self.name == 'time':
      # Sum of time for user, as days
      agg = sessions.aggregate(total=models.Sum('time'))
      nb = agg['total']
      return nb and nb.days or 0

    if self.name == 'age':
      # Membership age in years
      diff = timezone.now() - user.date_joined
      return diff.days / 365 # cast to int

    if self.name == 'premium':
      # Is user a premium paying member ?
      return user.subscriptions.filter(offer__slug='athlete', status='active').count()

    if self.name == 'trainer':
      # Nb of trained athletes, in all clubs
      from club.models import ClubMembership
      return ClubMembership.objects.filter(trainers=user).count()

    return 0.0

  def find_badges(self, user, save=False):
    '''
    Find the best badges for an user
    Optionally save them
    '''
    # Search badges
    val = self.get_user_value(user)
    if not val:
      return None, None
    badges = self.badges.filter(value__lte=val)

    # Save badges
    added_badges = []
    if save:
      for b in badges:
        try:
          BadgeUser.objects.create(user=user, badge=b)
          added_badges.append(b)
        except IntegrityError:
          pass # If badge already exist

    return badges, added_badges

class Badge(models.Model):
  '''
  Badge earned by users after some events
  '''
  name = models.CharField(max_length=250, unique=True)
  value = models.CharField(max_length=250, blank=True, null=True)
  category = models.ForeignKey(BadgeCategory, related_name='badges')
  position = models.IntegerField()
  users = models.ManyToManyField('users.Athlete', through='badges.BadgeUser', related_name='badges')

  def __unicode__(self):
    return u'%s : %s #%d' % (self.category.name, self.name, self.position)

  class Meta:
    ordering = ('position', )
    unique_together = (
      ('category', 'position'),
    )

class BadgeUser(models.Model):
  '''
  Link between a badge & user
  '''
  badge = models.ForeignKey(Badge)
  user = models.ForeignKey('users.Athlete')
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = (
      ('badge', 'user'),
    )

