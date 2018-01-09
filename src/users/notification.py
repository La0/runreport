# coding:utf-8
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import uuid

NOTIFICATION_COMMENT = 'comment'
NOTIFICATION_MAIL = 'mail'
NOTIFICATION_FRIEND_REQUEST = 'friend_request'
NOTIFICATION_PLAN_SESSION_APPLIED = 'plan_session_applied'
NOTIFICATION_PLAN_APP_REMOVED = 'plan_app_removed'
NOTIFICATION_DEMO_COMPLETE = 'demo'


class UserNotifications(object):
    user = None
    key_data = 'notification:%s'
    key_total = 'notification:%s:total'

    def __init__(self, user):
        self.user = user
        self.key_data = self.key_data % (self.user.username, )
        self.key_total = self.key_total % (self.user.username, )

    def add(self, category, message, context, link=None):
        # Build payload
        payload = {
            'category': category,
            'message': message,
            'context': context,
            'link': link,
            'created': datetime.now(),
            'id': uuid.uuid1().hex,  # Add a unique id for identification
        }

        # Add on top of notifications
        notifications = self.fetch()
        notifications.insert(0, payload)

        # Save it !
        self.store(notifications)

    def add_message(self, message):
        from messages.models import TYPE_COMMENTS_PRIVATE, TYPE_MAIL, TYPE_COMMENTS_WEEK

        # Check writer is not recipient : no notification
        if message.writer == self.user:
            return

        # Helper to add a message notification
        if message.conversation.type == TYPE_MAIL:
            # Direct user message
            msg = _('%(first_name)s %(last_name)s has sent you a message')
            context = {
                'first_name': message.writer.first_name,
                'last_name': message.writer.last_name,
            }

            # Direct to inbox
            link = reverse(
                'conversation-view',
                args=(
                    message.conversation.pk,
                ))

            # Category
            cat = NOTIFICATION_MAIL
        elif message.conversation.type == TYPE_COMMENTS_WEEK:
            week = message.conversation.week
            # Comment
            context = {
                'first_name': message.writer.first_name,
                'last_name': message.writer.last_name,
                'week': str(week),
            }
            if week.user == self.user:
                msg = _(
                    '%(first_name)s %(last_name)s has written a comment on your week %(week)s')
            else:
                msg = _(
                    '%(first_name)s %(last_name)s has written a comment on his week %(week)s')

            # Week link
            link = reverse(
                'user-calendar-week',
                args=(
                    week.user.username,
                    week.year,
                    week.week))

            # Category
            cat = NOTIFICATION_COMMENT

        else:
            # Comment
            is_private = message.conversation.type == TYPE_COMMENTS_PRIVATE
            session = message.conversation.get_session()
            context = {
                'first_name': message.writer.first_name,
                'last_name': message.writer.last_name,
                'name': session.name,
                'type': is_private and _(' private') or '',
            }
            session_user = session.day.week.user
            if session_user == message.writer:
                # its own session
                msg = _(
                    '%(first_name)s %(last_name)s has written a comment %(type)s on his session "%(name)s"')
            elif session_user == self.user:
                # your session
                msg = _(
                    '%(first_name)s %(last_name)s has written a comment %(type)s on your session "%(name)s"')
            else:
                # anyone else session
                msg = _(
                    '%(first_name)s %(last_name)s has written a comment on the session "%(name)s" of %(first_name)s %(last_name)s')
                context.update({
                    'first_name': session_user.first_name,
                    'last_name': session_user.last_name,
                })

            # Build session link
            link = reverse(
                'user-calendar-day',
                args=(
                    session_user.username,
                    session.day.date.year,
                    session.day.date.month,
                    session.day.date.day))
            link += '#conversation-%d-%s' % (session.pk,
                                             is_private and 'private' or 'public')

            # Category
            cat = NOTIFICATION_COMMENT

        # Add notification
        self.add(cat, msg, context, link)

    def add_friend_request(self, req, accepted=False):
        # Add a friend request notification
        if accepted:
            context = {
                'first_name': req.recipient.first_name,
                'last_name': req.recipient.last_name,
            }
            msg = _('%(first_name)s %(last_name)s is now your friend on RunReport')
            link = reverse(
                'user-public-profile',
                args=(
                    req.recipient.username,
                ))
        else:
            context = {
                'first_name': req.sender.first_name,
                'last_name': req.sender.last_name,
            }
            msg = _('%(first_name)s %(last_name)s wants to add you as a friend.')
            link = reverse('friends')

        self.add(NOTIFICATION_FRIEND_REQUEST, msg, context, link)

    def add_plan_session_applied(self, psa):
        # Add a PlanSession applied notification
        day = psa.sport_session.day
        athlete = day.week.user
        context = {
            'first_name': athlete.first_name,
            'last_name': athlete.last_name,
            'session_name': psa.plan_session.name,
        }
        if psa.status == 'done':
            msg = _(
                '%(first_name)s %(last_name)s has done his training : %(session_name)s')
        else:
            msg = _(
                '%(first_name)s %(last_name)s has missed his training : %(session_name)s')
        link = reverse(
            'user-calendar-day',
            args=(
                athlete.username,
                day.date.year,
                day.date.month,
                day.date.day))

        self.add(NOTIFICATION_PLAN_SESSION_APPLIED, msg, context, link)

    def add_plan_application_removed(self, app):
        # Notify when an athlete removes a plan
        athlete = app.user
        context = {
            'first_name': athlete.first_name,
            'last_name': athlete.last_name,
            'plan_name': app.plan.name,
        }
        msg = _(
            '%(first_name)s %(last_name)s has removed your plan %(plan_name)s from his calendar')

        self.add(NOTIFICATION_PLAN_SESSION_APPLIED, msg, context)

    def add_demo_completion(self, mode):
        '''
        Notify when a trainer or athlete
        completes a demo
        '''
        if mode == 'athlete':
            msg = _('Congratulations, you completed the RunReport demo for athletes.')
        elif mode == 'trainer':
            msg = _('Congratulations, you completed the RunReport demo for trainers.')
        else:
            raise Exception('Unsupported mode')

        self.add(NOTIFICATION_DEMO_COMPLETE, msg, {})

    def total(self):
        return cache.get(self.key_total) or 0

    def fetch(self):
        # Fetch raw data
        return cache.get(self.key_data) or []

    def store(self, data):
        # Save total & data, no expiry
        cache.set(self.key_total, len(data), None)
        return cache.set(self.key_data, data, None)

    def get(self, notification_id):
        # Search notification by its id
        for n in self.fetch():
            if n['id'] == notification_id:
                return n
        return None

    def clear(self, notification_id):
        n = self.get(notification_id)
        if not n:
            return None

        # Delete one notification
        notifications = self.fetch()
        notifications.remove(n)
        self.store(notifications)

        return n

    def clear_all(self):
        # Delete all notifications
        self.store([])
