from django.conf.urls import url, include
from sport.api import StatsView, SportList

user_urls = [
    url(r'^stats/$', StatsView.as_view(), name='stats'),
]

urlpatterns = [

    # Configuration
    url(r'^sport/', SportList.as_view(), name='sports'),

    # Endpoints per user
    url(r'^user/(?P<username>[\w\_\-]+)/', include(user_urls)),
]
