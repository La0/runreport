from django.conf.urls import patterns, url, include
from plan.views import *


urlpatterns = patterns('',

                       # Export plan as pdf file
                       url(r'^(?P<pk>\d+)/export/pdf/?',
                           PlanPdfExport.as_view(), name="plan-export-pdf"),

                       # Export plan as ics calendar file
                       url(r'^(?P<pk>\d+)/export/ics/?',
                           PlanIcsExport.as_view(),
                           name="plan-export-ics"),

                       # Move a plan session
                       url(r'^move/session/?',
                           MovePlanSession.as_view(),
                           name='plan-session-move'),

                       # Delete a plan application
                       url(r'^(?P<pk>\d+)/remove/?',
                           PlanApplicationDelete.as_view(),
                           name='plan-application-delete'),

                       # View plan (read only for athletes)
                       url(r'^(?P<pk>\d+)/?', PlanDetails.as_view(), name="plan"),

                       )
