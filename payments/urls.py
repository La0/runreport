from django.conf.urls import patterns, url
from payments.views import *

urlpatterns = patterns('',

  # Pay an offer
  url(r'^(?P<slug>\w+)/?$', PaymentOfferPay.as_view(), name="payment-offer"),
  url(r'^(?P<slug>\w+)/(?P<club_slug>[\w\_]+)/?$', PaymentOfferPay.as_view(), name="payment-offer-club"),

  # Payment status
  url(r'^/?$', PaymentStatus.as_view(), name="payment-status"),
)
