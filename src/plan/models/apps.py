# coding=utf-8
from django.db import models
from sport.models import SportSession
from users.notification import UserNotifications
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


PLAN_SESSION_APPLICATIONS = (
    ('applied', _('Applied')),  # Just applied by trainer
    ('done', _('Done')),  # Success
    ('failed', _('Failed')),  # Failed the plan
)


class PlanApplied(models.Model):
    '''
    Links a Plan to a User
    Shows global status of a plan application
    '''
    plan = models.ForeignKey('plan.Plan', related_name='applications')
    user = models.ForeignKey('users.Athlete', related_name='plans_applied')

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'plan'), )

    @property
    def status(self):
        '''
        Calc stats about sessions & theirs status
        '''
        out = {}
        for s, _name in PLAN_SESSION_APPLICATIONS:
            out[s] = self.sessions.filter(status=s).count()
        return out


class PlanSessionApplied(models.Model):
    '''
    Links a PlanSession to a SportSession
    '''
    # Links
    application = models.ForeignKey(PlanApplied, related_name='sessions')
    plan_session = models.ForeignKey(
        'plan.PlanSession',
        related_name='applications')
    sport_session = models.OneToOneField(
        'sport.SportSession', related_name='plan_session')

    # Validation
    status = models.CharField(
        max_length=20,
        choices=PLAN_SESSION_APPLICATIONS,
        default='applied')
    validated = models.DateTimeField(null=True, blank=True)

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    trainer_notified = models.DateTimeField(null=True, blank=True)

    def move(self, date):
        '''
        Move to another day the plan session application
        '''
        # Retrieve new day
        day = self.plan_session._build_day(self.application.user, date)

        # Build session
        defaults = {
            'name': self.plan_session.name,
            'distance': self.plan_session.distance,
            'time': self.plan_session.time,
        }
        session, _ = SportSession.objects.exclude(plan_session__isnull=False).get_or_create(
            sport=self.plan_session.sport, day=day, type=self.plan_session.type, defaults=defaults)

        # Save empty session for later deletion
        to_delete = None
        if (not self.sport_session.comment or self.sport_session.comment == '') \
                and not self.sport_session.distance and not self.sport_session.time:
            to_delete = self.sport_session

        # Update session attached
        self.sport_session = session
        self.save()

        # Delete after replacement
        if to_delete:
            to_delete.delete()

        return session

    def notify_trainer(self):
        '''
        Notify trainer of new validation from user
        '''
        if self.status == 'applied':
            raise Exception('Invalid status')

        # Send UserNotification
        un = UserNotifications(self.plan_session.plan.creator)
        un.add_plan_session_applied(self)

        # Update notification date
        self.trainer_notified = timezone.now()
        self.save()
