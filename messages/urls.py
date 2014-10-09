from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from messages.views import *

urlpatterns = patterns('',

  # Edit message
  url(r'^edit/(?P<message_id>\d+)', login_required(MessageEdit.as_view()), name="message-edit"),

  # Delete message
  url(r'^delete/(?P<message_id>\d+)', login_required(MessageDelete.as_view()), name="message-delete"),

  # User message
  url(r'^add/user/(?P<username>[\w_]+)', login_required(MessageUserAdd.as_view()), name="message-user-add"),

  # Comment add on SportSession
  url(r'^add/session/(?P<session_id>\d+)', login_required(MessageSessionAdd.as_view()), name="message-session-add"),

  # List messages from a SportSession
  url(r'^list/session/(?P<session_id>\d+)/(?P<type>all|private|public)', login_required(MessageSessionList.as_view()), name="message-session-list"),

  url(r'^/?$', login_required(MessageInbox.as_view()), name="message-inbox"),
)
