from django.conf.urls import patterns, url
from payments.views import *

urlpatterns = patterns('',

  # Pay an offer
  url(r'^(?P<slug>\w+)/?$', PaymentOfferPay.as_view(), name="payment-offer"),

  # Payment status
  url(r'^/?$', PaymentStatus.as_view(), name="payment-status"),
)
