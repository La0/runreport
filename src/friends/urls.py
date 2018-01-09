from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from friends.views import *

urlpatterns = [

    # Friend requests
    url(r'^add/(?P<username>[\w\_]+)/?',
        login_required(FriendAdd.as_view()),
        name="friend-add"),
    url(r'^delete/(?P<username>[\w\_]+)/?',
        login_required(FriendDelete.as_view()),
        name="friend-delete"),
    url(r'^request/(?P<username>\w+)/(?P<action>accept|refuse)/?',
        login_required(FriendRequestChoice.as_view()), name="friend-request"),

    # Friends home
    url(r'^/?$',
        login_required(FriendsHome.as_view()),
        name="friends"),
]
