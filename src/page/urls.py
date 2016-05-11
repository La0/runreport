from django.conf.urls import patterns, url
from page.views import *

urlpatterns = patterns('',
  url(r'^/?$', PageList.as_view(), name="page-list"),
  url(r'^(?P<slug>[\w_]+)/?$', PageDetail.as_view(), name="page"),
)
