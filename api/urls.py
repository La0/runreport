from django.conf.urls import patterns, url
from api import views
from rest_framework import routers

# Add viewsets
router = routers.SimpleRouter()
router.register(r'plans', views.PlanViewSet, base_name='plan')
urlpatterns = router.urls

# Add direct views
urlpatterns += patterns('',

  # Connected user
  url(r'user/', views.AthleteDetails.as_view(), name='user'),
)

