from django.conf.urls import patterns, url
from payments.views import PaymentCardView, Payment3DsView

urlpatterns = patterns('',

    # Add a credit card for a club
    url(r'^card/(?P<slug>[\w\_\-]+)/?', PaymentCardView.as_view(), name='payment-card'),

    # 3D secure validation return
    url(r'^3ds/(?P<slug>[\w\_\-]+)/(?P<card_id>\d+)/(?P<hash>\w+)/?', Payment3DsView.as_view(), name='payment-3ds'),
)
