from django.views.generic import DeleteView
from messages.models import Message
from mixins import MessageReloadMixin, MessageOwned

class MessageDelete(MessageReloadMixin, MessageOwned, DeleteView):
  model = Message
  template_name = 'messages/delete.html'

  def delete(self, *args, **kwargs):
    # Delete message
    message = self.get_object()
    session = message.session
    message.delete()

    return self.reload(session)
