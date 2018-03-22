from django.conf.urls import url, include
from sport.api import StatsView, SportList, CalendarYear, CalendarMonth, CalendarWeek, CalendarDay, SessionManage, SessionCreate

user_urls = [

    # User calendar
    url(r'^year/(?P<year>\d+)/$', CalendarYear.as_view(), name='year'),
    url(r'^month/(?P<year>\d+)/(?P<month>\d+)/$', CalendarMonth.as_view(), name='month'),
    url(r'^week/(?P<year>\d+)/(?P<week>\d+)/$', CalendarWeek.as_view(), name='week'),
    url(r'^day/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', CalendarDay.as_view(), name='day'),

    # User Stats
    url(r'^stats/$', StatsView.as_view(), name='stats'),
]

session_urls = [
    url(r'^(?P<pk>\d+)/$', SessionManage.as_view(), name='session'),
    url(r'^$', SessionCreate.as_view(), name='session-create'),
]

urlpatterns = [

    # Configuration
    url(r'^sport/', SportList.as_view(), name='sports'),

    # Endpoints per user
    url(r'^user/(?P<username>[\w\_\-]+)/', include(user_urls)),

    # Sessions
    url(r'^session/', include(session_urls)),
]
