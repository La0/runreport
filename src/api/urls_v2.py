from django.conf.urls import url, include
from sport.api import StatsView

user_urls = [
    url(r'^stats/$', StatsView.as_view(), name='stats'),
]

urlpatterns = [

    # Endpoints per user
    url(r'^user/(?P<username>[\w\_\-]+)/', include(user_urls)),
]
