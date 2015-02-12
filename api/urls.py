from django.conf.urls import patterns, url
from api import views
#from rest_framework import routers
from rest_framework_nested import routers

# Add viewsets through routers
plan_router = routers.SimpleRouter()
plan_router.register(r'plans', views.PlanViewSet, base_name='plan')

sessions_router = routers.NestedSimpleRouter(plan_router, r'plans', lookup='plan')
sessions_router.register(r'sessions', views.PlanSessionViewSet, base_name='session')

sports_router = routers.SimpleRouter()
sports_router.register(r'sports', views.SportViewSet, base_name='sport')

clubs_router = routers.SimpleRouter()
clubs_router.register(r'clubs', views.ClubMembershipViewSet, base_name='club')

urlpatterns = plan_router.urls + sessions_router.urls + sports_router.urls + clubs_router.urls

# Add direct views
urlpatterns += patterns('',

  # Connected user
  url(r'user/', views.AthleteDetails.as_view(), name='user'),

  # Publish a plan to users
  url(r'^plans/(?P<pk>[\d]+)/publish/', views.PlanPublishView.as_view(), name='plan-publish'),

  # Copy a plan
  url(r'^plans/(?P<pk>[\d]+)/copy/', views.PlanCopyView.as_view(), name='plan-copy'),
)

