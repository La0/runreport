from coffin.conf.urls import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from views import *

urlpatterns = patterns('',
  url(r'^login/?$', LoginUser.as_view(), name='login'),
  url(r'^profile/?$', login_required(Profile.as_view()), name='user-profile'),
  url(r'^garmin/?$', login_required(GarminLogin.as_view()), name='user-garmin'),
  url(r'^create/?$', CreateUser.as_view(), name='user-create'),
  url(r'^logout/?$', LogoutUser.as_view(), name='logout'),

  # Races
  url(r'^races/?$', login_required(RacesView.as_view()), name='user-races'),

  # Password Management
  url(r'^password/update/?$', login_required(UpdatePassword.as_view()), name='user-password-update'),
  url(r'^password/reset/?$', password_reset, name='user-password-reset', kwargs={
    'template_name' : 'users/password_reset_form.html',
    'subject_template_name' : 'users/password_reset_subject.txt',
    'email_template_name' : 'users/password_reset_email.html',
  }),
  url(r'^password/confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$', password_reset_confirm, name='user-password-reset-confirm', kwargs={
    'template_name' : 'users/password_reset_confirm.html',
  }),
  url(r'^password/complete/?$', password_reset_complete, name='user-password-reset-complete', kwargs={
    'template_name' : 'users/password_reset_complete.html',
  }),
  url(r'^password/done/?$', password_reset_done, name='user-password-reset-done', kwargs={
    'template_name' : 'users/password_reset_done.html',
  }),
)
