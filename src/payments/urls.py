from django.conf.urls import patterns, url
from payments.views import PaymentCardView, Payment3DsView, PaymentNotification, PaymentPeriodView, PaymentPeriodExport

urlpatterns = patterns('',

                       # Add a credit card for a club
                       url(r'^card/(?P<slug>[\w\_\-]+)/?',
                           PaymentCardView.as_view(),
                           name='payment-card'),

                       # 3D secure validation return
                       url(r'^3ds/(?P<slug>[\w\_\-]+)/(?P<card_id>\d+)/(?P<hash>\w+)/?',
                           Payment3DsView.as_view(), name='payment-3ds'),

                       # Notifications from Mangopay
                       url(r'^notification/(?P<hash>\w+)/',
                           PaymentNotification.as_view(),
                           name='payment-notification'),

                       # Pay a specified period (error management)
                       #url(r'^pay/(?P<pk>\d+)/',
                       #    PaymentPeriodView.as_view(),
                       #    name='payment-period'),

                       # Download the pdf of a bill
                       url(r'^export/(?P<pk>\d+)/',
                           PaymentPeriodExport.as_view(),
                           name='payment-export'),
                       )
