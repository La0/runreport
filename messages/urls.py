from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from messages.views import *

urlpatterns = patterns('',

  # Edit message
  url(r'^edit/(?P<message_id>\d+)', login_required(MessageEdit.as_view()), name="message-edit"),

  # Delete message
  url(r'^delete/(?P<message_id>\d+)', login_required(MessageDelete.as_view()), name="message-delete"),

  # Add messages
  # From user profile
  url(r'^add/user/(?P<username>[\w_]+)', login_required(MessageUserAdd.as_view()), name="message-user-add"),
  # From sport session
  url(r'^add/session/(?P<session_id>\d+)/(?P<type>\w+)', login_required(MessageSessionAdd.as_view()), name="message-session-add"),
  # From sport week
  url(r'^add/week/(?P<week_id>\d+)', login_required(MessageWeekAdd.as_view()), name="message-week-add"),
  # From conversation
  url(r'^add/conversation/(?P<conversation_id>\d+)', login_required(ConversationAdd.as_view()), name="conversation-add"),

  # List messages from a Conversation
  url(r'^list/(?P<conversation_id>\d+)/full/?', ConversationList.as_view(), {'full' : True, },  name="conversation-list-full"),
  url(r'^list/(?P<conversation_id>\d+)/?', ConversationList.as_view(), {'full' : False, }, name="conversation-list"),

  # User inbox
  url(r'^(?P<conversation_id>\d+)/?$', login_required(ConversationView.as_view()), name="conversation-view"),
  url(r'^page/(?P<page>\d+)/?$', login_required(MessageInbox.as_view()), name="message-inbox-page"),
  url(r'^/?$', login_required(MessageInbox.as_view()), name="message-inbox"),
)
