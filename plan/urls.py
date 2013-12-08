from django.conf.urls import patterns, url, include
from plan.views import *


plan_urls = patterns('plan', 
  # Week actions
  url(r'week/add/?', PlanWeekDetails.as_view(), {'action':'add'}, name="plan-week-add"),
  url(r'week/(?P<week>\d+)/delete/?', PlanWeekDetails.as_view(), {'action':'delete'}, name="plan-week-delete"),

  # Day
  url(r'day/(?P<week>\d+)/(?P<day>\d+)/?$', PlanDay.as_view(), name="plan-day"), 

  # Details
  url(r'/?$', PlanDetails.as_view(), name="plan"), 
)

urlpatterns = patterns('',
  url(r'^/?$', PlanList.as_view(), name="plans"),
  url(r'new/?', PlanCreate.as_view(), name="plan-new"), 

  # Plan details
  url(r'(?P<slug>\w+)/', include(plan_urls)),
)
