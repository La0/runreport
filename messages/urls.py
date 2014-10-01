from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from messages.views import *

urlpatterns = patterns('',
  url(r'^/?$', login_required(MessageInbox.as_view()), name="message-inbox"),
)
