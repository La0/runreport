from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from messages.views import *

urlpatterns = patterns('',
  url(r'^/?$', login_required(MessageInbox.as_view()), name="message-inbox"),

  # Comment add
  url(r'^add/session/(?P<session_id>\d+)', login_required(MessageSessionAdd.as_view()), name="message-session-add"),
)
