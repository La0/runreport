# coding:utf-8
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import uuid

NOTIFICATION_COMMENT = 'comment'
NOTIFICATION_MAIL = 'mail'
NOTIFICATION_FRIEND_REQUEST = 'friend_request'


class UserNotifications(object):
  user = None
  key_data = 'notification:%s'
  key_total = 'notification:%s:total'


  def __init__(self, user):
    self.user = user
    self.key_data = self.key_data % (self.user.username, )
    self.key_total = self.key_total % (self.user.username, )

  def add(self, category, description, link=None):
    # Build payload
    payload = {
      'category' : category,
      'description' : description,
      'link' : link,
      'created' : datetime.now(),
      'id' : uuid.uuid1().hex, # Add a unique id for identification
    }

    # Add on top of notifications
    notifications = self.fetch()
    notifications.insert(0, payload)

    # Save it !
    self.store(notifications)

  def add_message(self, message):
    from messages.models import TYPE_COMMENTS_PUBLIC, TYPE_COMMENTS_PRIVATE, TYPE_MAIL

    # Check writer is not recipient : no notification
    if message.writer == self.user:
      return

    # Helper to add a message notification
    if message.conversation.type == TYPE_MAIL:
      # Direct user message
      msg = _('%(first_name)s %(last_name)s has sent you a message') % {
        'first_name' : message.writer.first_name,
        'last_name' : message.writer.last_name,
      }

      # Direct to inbox
      link = reverse('conversation-view', args=(message.conversation.pk, ))

      # Category
      cat = NOTIFICATION_MAIL
    else:
      # Comment
      msg = _('%(first_name)s %(last_name)s has written a comment') % {
        'first_name' : message.writer.first_name,
        'last_name' : message.writer.last_name,
      }
      is_private = message.conversation.type == TYPE_COMMENTS_PRIVATE
      session = message.conversation.get_session()
      session_user = session.day.week.user
      if session_user == message.writer:
        # its own session
        msg += _('%(type)s on his session "%(name)s"') % {
          'type' : is_private and _(' private') or '',
          'name' : session.name,
        }
      elif session_user == self.user:
        # your session
        msg += _('%(type)s on your session "%(name)s"') % {
          'type' : is_private and _(' private') or '',
          'name' : session.name,
        }
      else:
        # anyone else session
        msg += _(' on the session "%(name)s" of %(first_name)s %(last_name)s') % {
          'name' : session.name,
          'first_name' : session_user.first_name,
          'last_name' : session_user.last_name,
        }

      # Build session link
      link = reverse('user-calendar-day', args=(session_user.username, session.day.date.year, session.day.date.month, session.day.date.day))
      link += '#conversation-%d-%s' % (session.pk, is_private and 'private' or 'public')

      # Category
      cat = NOTIFICATION_COMMENT

    # Add notification
    self.add(cat, msg, link)

  def add_friend_request(self, req, accepted=False):
    # Add a friend request notification
    if accepted:
      msg = _('%(first_name)s %(last_name)s is now your friend on RunReport') % {
        'first_name' : req.recipient.first_name,
        'last_name' : req.recipient.last_name,
      }
      link = reverse('user-public-profile', args=(req.recipient.username, ))
    else:
      msg = _('%(first_name)s %(last_name)s wants to add you as a friend.') % {
        'first_name' : req.recipient.first_name,
        'last_name' : req.recipient.last_name,
      }
      link = reverse('friends')

    self.add(NOTIFICATION_FRIEND_REQUEST, msg, link)

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
