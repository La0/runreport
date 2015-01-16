from django.conf.urls import patterns, url, include
from api import views

urlpatterns = patterns('',

  # Connected user
  url(r'user/', views.AthleteDetails.as_view(), name='user'),

  # Browser Auth
  #url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
)

