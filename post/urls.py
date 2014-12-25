from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from post.views import *

urlpatterns = patterns('',

  # Post edition
  url(r'^new/?', login_required(PostCreateView.as_view()), name="post-create"),
  url(r'^(?P<slug>[\w_]+)/edit/?', login_required(PostEditView.as_view()), name="post-edit"),
  url(r'^(?P<slug>[\w_]+)/sessions/?', login_required(PostSessionsView.as_view()), name="post-sessions"),

  # List user's personal posts
  url(r'^/?$', login_required(PostListView.as_view()), name="posts"),
)
