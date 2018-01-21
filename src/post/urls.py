from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from post.views import *

urlpatterns = [

    # Post edition
    url(r'^(?P<slug>[\w_]+)/sessions/?',
        login_required(PostSessionsView.as_view()),
        name="post-sessions"),

    # Post Medias
    url(r'^media/(?P<pk>\d+)/delete/?',
        login_required(PostMediaDeleteView.as_view()),
        name="post-media-delete"),

    # List user's personal posts
    url(r'^$',
        login_required(PostListView.as_view()),
        name="posts"),
]
