from django.views.generic import ListView
from django.db.models import Q, Max
from messages.models import Conversation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class MessageInbox(ListView):
  template_name = 'messages/inbox.html'
  context_object_name = 'conversations'

  def get_queryset(self):
    # List conversations, last messages first
    conversations = Conversation.objects.filter(
      Q(mail_recipient=self.request.user) | \
      Q(session_user=self.request.user) | \
      Q(messages__writer=self.request.user) \
    )
    conversations = conversations.prefetch_related('messages', 'messages__writer')
    # Annotate with last message date
    conversations = conversations.annotate(last_message=Max('messages__created'))
    conversations = conversations.distinct().order_by('-last_message')


    # Paginate: 10 conversations per page
    paginator = Paginator(conversations, 10)
    page = self.kwargs.get('page', 1)
    try:
      conversations = paginator.page(page)
    except PageNotAnInteger:
      # If page is not an integer, deliver first page.
      conversations = paginator.page(1)
    except EmptyPage:
      # If page is out of range (e.g. 9999), deliver last page of results.
      conversations = paginator.page(paginator.num_pages)

    return conversations
