from rest_framework import views, response, exceptions
from django.core.exceptions import PermissionDenied
from payments.models import PaymentOffer
from club.models import Club
import logging

logger = logging.getLogger('payments')


class PaymentTokenView(views.APIView):
  '''
  Create a transaction from a Paymill token
  '''
  def post(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    try:
      # Load offer
      offer_slug = request.POST.get('offer')
      offer = PaymentOffer.objects.get(slug=offer_slug)

      # Load club
      club_slug = request.POST.get('club')
      club = None
      if offer.target == 'club' and club_slug:
        club = Club.objects.get(pk=club_slug, manager=request.user)

      # Create client on user
      if not request.user.paymill_id:
        request.user.sync_paymill()

      # Create subscription with client & offer
      offer.create_subscription(request.POST.get('token'), request.user, club=club)

    except Exception, e:
      logger.error('Payment error for %s: %s' % (request.user, e.message))

      # Handle paymill errors
      if isinstance(e.message, dict) and 'error' in e.message:
        msg = e.message['error']
      else:
        msg = e.message
      raise exceptions.APIException(msg)

    # Return dummy status
    return response.Response({'payment' : True})
