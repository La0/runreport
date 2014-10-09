from coach.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_REDIRECT_SKIP
from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect
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

class UserNotificationsClear(JsonResponseMixin, View):
  def get(self, *args, **kwargs):
    un = UserNotifications(self.request.user)
    if 'uuid' in self.kwargs:
      # Clear one notification
      notif = un.clear(self.kwargs['uuid'])

      # Redirect to link if any
      if notif and 'link' in notif:
        self.json_options = [JSON_OPTION_REDIRECT_SKIP , ]
        return HttpResponseRedirect(notif['link'])
    else:
      # Clear all notifications
      un.clear_all()

    # Reload whole page
    self.json_options = [JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD, ]
    return self.render_to_response({})
