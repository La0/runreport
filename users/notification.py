# coding:utf-8
from django.core.cache import cache
from django.core.urlresolvers import reverse
from datetime import datetime
import uuid

NOTIFICATION_COMMENT = 'comment'
NOTIFICATION_MAIL = 'mail'


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

    # Check sender is not recipient : no notification
    if message.sender == self.user:
      return

    # Helper to add a message notification
    if message.session:
      # Comment
      msg = u'%s %s a laissé un commentaire' % (message.sender.first_name, message.sender.last_name)
      if message.recipient == message.sender:
        # its own session
        msg += u'%s sur sa séance "%s"' % (message.private and u' privé' or '', message.session.name,)
      elif message.recipient == self.user:
        # your session
        msg += u'%s sur votre séance "%s"' % (message.private and u' privé' or '', message.session.name,)
      else:
        # anyone else session
        msg += u' sur la séance "%s" de %s %s' % (message.session.name, message.recipient.first_name, message.recipient.last_name )
    else:
      # Direct user message
      msg = u'%s %s vous a envoyé un message' % (message.sender.first_name, message.sender.last_name)

    if message.session:
      # Build session link
      day = message.session.day
      link = reverse('user-calendar-day', args=(day.week.user.username, day.date.year, day.date.month, day.date.day))
    else:
      # Direct to inbox
      link = reverse('message-inbox')

    # Add notification
    cat = message.session and NOTIFICATION_COMMENT or NOTIFICATION_MAIL
    self.add(cat, msg, link)

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
