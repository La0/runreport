from django.conf.urls import patterns, url
from plan.views import *

urlpatterns = patterns('',
  url(r'^/?$', PlanList.as_view(), name="plans"),
  url(r'new/?', PlanCreate.as_view(), name="plan-new"), 
  url(r'(?P<pk>\d+)/?', PlanDetails.as_view(), name="plan"), 
)
