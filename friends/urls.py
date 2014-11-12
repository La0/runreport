from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from friends.views import *

urlpatterns = patterns('',

  # Friend requests
  url(r'^add/(?P<username>[\w\_]+)/?', login_required(FriendAdd.as_view()), name="friend-add"),

  # Friends home
  url(r'^/?$', login_required(FriendsHome.as_view()), name="friends"),
)
