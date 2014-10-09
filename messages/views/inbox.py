from django.views.generic import ListView

class MessageInbox(ListView):
  template_name = 'messages/inbox.html'
  context_object_name = 'messages'

  def get_queryset(self):
    messages = self.request.user.messages_received
    messages = messages.exclude(sender=self.request.user)
    messages = messages.order_by('-created')
    return messages
