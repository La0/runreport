from django.views.generic import ListView
from coach.mixins import JsonResponseMixin
from mixins import MessageSessionReload, MessageSessionMixin

class MessageSessionList(JsonResponseMixin, MessageSessionMixin, ListView):
  template_name = 'messages/_list.html'
  context_object_name = 'messages'

  def get_queryset(self):
    session = self.get_session()
    return session.comments.order_by('created')
