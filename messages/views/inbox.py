from django.views.generic import ListView

class MessageInbox(ListView):
  template_name = 'messages/inbox.html'
  context_object_name = 'messages'

  def get_queryset(self):
    return self.request.user.messages_received.order_by('-created')
