from django.core.cache import cache
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

  def total(self):
    return cache.get(self.key_total) or 0

  def fetch(self):
    # Fetch raw data
    return cache.get(self.key_data) or []

  def store(self, data):
    # Save total & data
    cache.set(self.key_total, len(data))
    return cache.set(self.key_data, data)
