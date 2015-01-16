from django.conf.urls import patterns, url
from api import views

urlpatterns = patterns('',

  # Connected user
  url(r'user/', views.AthleteDetails.as_view(), name='user'),
)

