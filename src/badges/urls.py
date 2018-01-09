from django.conf.urls import url
from badges.views import *

urlpatterns = [
    url(r'^/?$', BadgesView.as_view(), name="badges"),
]
