from django.conf.urls import patterns, url, include
from payments.views import *

urlpatterns = patterns('',
  url(r'^(?P<slug>\w+)/pay?$', PaymentOfferPay.as_view(), name="payment-offer-pay"),
)
