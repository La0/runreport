from coach.mixins import JsonResponseMixin
from django.views.generic import TemplateView
from users.notification import UserNotifications

class UserNotificationsList(JsonResponseMixin, TemplateView):
  template_name = 'users/notifications.html'

  def get_context_data(self, *args, **kwargs):
    context = super(UserNotificationsList, self).get_context_data(*args, **kwargs)
    context.update(self.get_notifications())
    return context

  def get_notifications(self):
    un = UserNotifications(self.request.user)
    return {
      'total' : un.total(),
      'notifications' : un.fetch(),
    }
