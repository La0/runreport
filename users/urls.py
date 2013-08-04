from coffin.conf.urls import *
from django.contrib.auth.decorators import login_required
from views import *

urlpatterns = patterns('',
  url(r'^login/?$', LoginUser.as_view(), name='login'),
  url(r'^profile/?$', login_required(Profile.as_view()), name='user-profile'),
  url(r'^garmin/?$', login_required(GarminLogin.as_view()), name='user-garmin'),
  url(r'^create/?$', CreateUser.as_view(), name='user-create'),
  url(r'^logout/?$', LogoutUser.as_view(), name='logout'),
)
