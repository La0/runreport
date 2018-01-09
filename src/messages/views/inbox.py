from django.views.generic import ListView
from django.db.models import Q, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from messages.models import Conversation, TYPE_PLAN_SESSION
from users.models import Athlete


class MessageInbox(ListView):
    template_name = 'messages/inbox.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        # List conversations, last messages first
        conversations = Conversation.objects.filter(
            Q(mail_recipient=self.request.user) |
            Q(session_user=self.request.user) |
            Q(messages__writer=self.request.user)
        )
        conversations = conversations.exclude(type=TYPE_PLAN_SESSION)
        conversations = conversations.prefetch_related(
            'messages', 'messages__writer')
        # Annotate with last message date
        conversations = conversations.annotate(
            last_message=Max('messages__created'))
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
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            conversations = paginator.page(paginator.num_pages)

        return conversations


class ConversationsUserView(ListView):
    '''
    List conversations between a target
    and the current user
    '''
    template_name = 'messages/with.user.html'
    context_object_name = 'conversations'

    def get_context_data(self):
        context = super(ConversationsUserView, self).get_context_data()
        context['target'] = self.target
        return context

    def get_queryset(self):
        # Check the targetted use exists
        self.target = get_object_or_404(
            Athlete, username=self.kwargs['username'])

        # Load the conversations with these two
        qs = Conversation.objects.filter(messages__writer=self.request.user)
        qs = qs.filter(messages__writer=self.target)
        qs = qs.prefetch_related('messages', 'messages__writer')
        qs = qs.annotate(last_message=Max('messages__created'))
        qs = qs.distinct().order_by('-last_message')

        return qs
