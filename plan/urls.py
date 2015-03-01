from django.conf.urls import patterns, url, include
from plan.views import *


urlpatterns = patterns('',

  # Export plan as pdf file
  url(r'^(?P<pk>\d+)/export/pdf/?', PlanPdfExport.as_view(), name="plan-export-pdf"),

  # Export plan as ics calendar file
  url(r'^(?P<pk>\d+)/export/ics/?', PlanIcsExport.as_view(), name="plan-export-ics"),


  # View plan (read only for athletes)
  url(r'^(?P<pk>\d+)/?', PlanDetails.as_view(), name="plan"),

)
