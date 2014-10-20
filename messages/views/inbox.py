from django.views.generic import ListView
from django.db.models import Q
from messages.models import Message

class MessageInbox(ListView):
  template_name = 'messages/inbox.html'
  context_object_name = 'messages'

  def get_queryset(self):
    messages = Message.objects.filter(Q(conversation__mail_recipient=self.request.user) | Q(conversation__session_user=self.request.user) | Q(conversation__messages__writer=self.request.user))
    messages = messages.exclude(writer=self.request.user)
    messages = messages.distinct().order_by('-created')
    return messages
