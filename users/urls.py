from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.views.generic.base import RedirectView
from views import *
from post.views import PostView

user_patterns = patterns('',
  # Calendar for a user
  url(r'^year/(?P<year>[\d]{4})/?', AthleteCalendarYear.as_view(), name="user-calendar-year"),
  url(r'^month/(?P<year>[\d]{4})/(?P<month>[\d]{1,2})/?', AthleteCalendarMonth.as_view(), name="user-calendar-month"),
  url(r'^week/(?P<year>[\d]{4})/(?P<week>[\d]{1,2})/?', AthleteCalendarWeek.as_view(), name="user-calendar-week"),
  url(r'^day/(?P<year>[\d]{4})/(?P<month>[\d]{1,2})/(?P<day>[\d]{1,2})/?', AthleteCalendarDay.as_view(), name="user-calendar-day"),

  # Stats for a user
  url(r'^stats/?$', AthleteStats.as_view(), name='athlete-stats'),
  url(r'^stats/all/?$', AthleteStats.as_view(), name='athlete-stats-all', kwargs={'all': True}),
  url(r'^stats/(?P<year>\d{4})/?$', AthleteStats.as_view(), name='athlete-stats-year'),

  # View post
  url(r'^post/(?P<slug>[\w_]+)/?$', PostView.as_view(), name='post'),

  url(r'^/?', PublicProfile.as_view(), name="user-public-profile"),
)

urlpatterns = patterns('',
  # Preferences, old & new
  url(r'^profile/?$', RedirectView.as_view(url='/user/preferences', permanent=True)),
  url(r'^preferences/?$', login_required(Preferences.as_view()), name='user-preferences'),

  url(r'^login/?$', LoginUser.as_view(), name='login'),
  url(r'^my-profile/?$', login_required(OwnProfile.as_view()), name='user-own-profile'),
  url(r'^garmin/?$', login_required(GarminLogin.as_view()), name='user-garmin'),
  url(r'^create/?$', CreateUser.as_view(), name='user-create'),
  url(r'^activate/?$', ActivateUser.as_view(), name='user-activate'),
  url(r'^logout/?$', LogoutUser.as_view(), name='logout'),

  # Races
  url(r'^races/?$', login_required(RacesView.as_view()), name='user-races'),

  # Password Management
  url(r'^password/update/?$', login_required(UpdatePassword.as_view()), name='user-password-update'),
  url(r'^password/reset/?$', password_reset, name='password_reset', kwargs={
    'template_name' : 'users/password_reset_form.html',
    'subject_template_name' : 'users/password_reset_subject.txt',
    'email_template_name' : 'users/password_reset_email.html',
  }),
  url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm', kwargs={
    'template_name' : 'users/password_reset_confirm.html',
  }),
  url(r'^password/complete/?$', password_reset_complete, name='password_reset_complete', kwargs={
    'template_name' : 'users/password_reset_complete.html',
  }),
  url(r'^password/done/?$', password_reset_done, name='password_reset_done', kwargs={
    'template_name' : 'users/password_reset_done.html',
  }),

  # Notifications
  url(r'^notification/list/?$', login_required(UserNotificationsList.as_view()), name="user-notifications"),
  url(r'^notification/clear/all/?$', login_required(UserNotificationsClear.as_view()), name="user-notifications-clear-all"),
  url(r'^notification/clear/(?P<uuid>[a-z0-9]+)/?$', login_required(UserNotificationsClear.as_view()), name="user-notifications-clear"),

  # Fallback to user public profile
  url(r'^(?P<username>[\w\_]+)/', include(user_patterns)),
)
