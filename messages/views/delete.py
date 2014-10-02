from django.views.generic import DeleteView
from django.shortcuts import get_object_or_404
from messages.models import Message
from mixins import MessageSessionReload

class MessageDelete(MessageSessionReload, DeleteView):
  model = Message
  template_name = 'messages/delete.html'

  def get_object(self):
    # Message must be owned by logged user
    return get_object_or_404(Message, pk=self.kwargs['message_id'], sender=self.request.user)

  def delete(self, *args, **kwargs):
    # Delete message
    message = self.get_object()
    session = message.session
    message.delete()

    return self.reload(session)
