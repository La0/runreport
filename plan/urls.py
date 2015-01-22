from django.conf.urls import patterns, url, include
from plan.views import *


urlpatterns = patterns('',

  # Export plan as pdf file
  url(r'^(?P<pk>\d+)/export/pdf/?', PlanPdfExport.as_view(), name="plan-export-pdf"),
)
