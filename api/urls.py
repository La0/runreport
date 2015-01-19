from django.conf.urls import patterns, url
from api import views
#from rest_framework import routers
from rest_framework_nested import routers

# Add viewsets through routers
plan_router = routers.SimpleRouter()
plan_router.register(r'plans', views.PlanViewSet, base_name='plan')

sessions_router = routers.NestedSimpleRouter(plan_router, r'plans', lookup='plan')
sessions_router.register(r'sessions', views.PlanSessionViewSet, base_name='session')

urlpatterns = plan_router.urls + sessions_router.urls

# Add direct views
urlpatterns += patterns('',

  # Connected user
  url(r'user/', views.AthleteDetails.as_view(), name='user'),
)

