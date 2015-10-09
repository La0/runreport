from django.conf.urls import patterns, url
from payments.views import *

urlpatterns = patterns('',
  # Cancel a subscription
  url(r'^(?P<slug>\w+)/cancel/?$', PaymentOfferCancel.as_view(), name="payment-sub-delete"),

  # Pay an offer
  url(r'^(?P<slug>\w+)/?$', PaymentOfferPay.as_view(), name="payment-offer"),
  url(r'^(?P<slug>\w+)/(?P<club_slug>[\w\-\_]+)/?$', PaymentOfferPay.as_view(), name="payment-offer-club"),
)
