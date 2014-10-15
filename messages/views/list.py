from django.views.generic import ListView
from coach.mixins import JsonResponseMixin
from mixins import MessageSessionMixin, ConversationMixin

class ConversationList(JsonResponseMixin, ConversationMixin, ListView):
  template_name = 'messages/_list.html'
  context_object_name = 'messages'
  list_type = None

  def get_context_data(self):
    context = super(ConversationList, self).get_context_data()

    # Current main conversation
    context['conversation'] = self.conversation
    context['session'] = self.session
    context['privacy'] = self.privacy

    # List all available conversations for user
    conversations = []
    if 'comments_private' in self.privacy and self.session.comments_private:
      conversations.append(self.session.comments_private)
    if 'comments_public' in self.privacy and self.session.comments_public:
      conversations.append(self.session.comments_public)
    context['conversations'] = conversations

    return context

  def get_queryset(self):
    # Load conversation
    self.get_conversation()

    # List its messages
    return self.conversation.messages.order_by('created')
