from django.conf.urls import url, include
from sport.api import StatsView, SportList, CalendarYear, CalendarMonth, CalendarWeek, CalendarDay

user_urls = [

    # User calendar
    url(r'^year/(?P<year>\d+)/$', CalendarYear.as_view(), name='year'),
    url(r'^month/(?P<year>\d+)/(?P<month>\d+)/$', CalendarMonth.as_view(), name='month'),
    url(r'^week/(?P<year>\d+)/(?P<week>\d+)/$', CalendarWeek.as_view(), name='week'),
    url(r'^day/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', CalendarDay.as_view(), name='day'),

    # User Stats
    url(r'^stats/$', StatsView.as_view(), name='stats'),
]

urlpatterns = [

    # Configuration
    url(r'^sport/', SportList.as_view(), name='sports'),

    # Endpoints per user
    url(r'^user/(?P<username>[\w\_\-]+)/', include(user_urls)),
]
