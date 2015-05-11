from django.conf.urls import patterns, url
from payments.views import *

urlpatterns = patterns('',

  # Payment status
  url(r'^status/?$', PaymentStatus.as_view(), name="payment-status"),

  # Pay an offer
  url(r'^(?P<slug>\w+)/?$', PaymentOfferPay.as_view(), name="payment-offer"),
)
