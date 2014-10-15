from django.views.generic import ListView
from messages.models import Message

class MessageInbox(ListView):
  template_name = 'messages/inbox.html'
  context_object_name = 'messages'

  def get_queryset(self):
    messages = Message.objects.filter(conversation__mail_recipient=self.request.user)
    messages = messages.order_by('-created')
    return messages
