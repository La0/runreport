# coding:utf-8
from django.core.cache import cache
from django.core.urlresolvers import reverse
from datetime import datetime
import uuid

NOTIFICATION_MESSAGE = 'message'


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
    msg = u'%s %s a laissé un commentaire' % (message.sender.first_name, message.sender.last_name)
    if message.session:
      msg += u' sur la séance "%s"' % (message.session.name, )

    # Build session link
    link = None
    if message.session:
      day = message.session.day
      link = reverse('user-calendar-day', args=(day.week.user.username, day.date.year, day.date.month, day.date.day))

    # Add notification
    self.add(NOTIFICATION_MESSAGE, msg, link)

  def total(self):
    return cache.get(self.key_total) or 0

  def fetch(self):
    # Fetch raw data
    return cache.get(self.key_data) or []

  def store(self, data):
    # Save total & data, no expiry
    cache.set(self.key_total, len(data), None)
    return cache.set(self.key_data, data, None)
