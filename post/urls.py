from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from post.views import *

urlpatterns = patterns('',

  # Post edition
  url(r'^new/?', login_required(PostCreateView.as_view()), name="post-create"),
  url(r'^(?P<slug>[\w_]+)/edit/?', login_required(PostEditView.as_view()), name="post-edit"),
)
