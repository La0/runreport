from rest_framework import views, response, exceptions
from django.core.exceptions import PermissionDenied
from payments.models import PaymentOffer


class PaymentTokenView(views.APIView):
  '''
  Create a transaction from a Paymill token
  '''
  def post(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    # Load offer
    try:
      offer_slug = request.POST.get('offer')
      offer = PaymentOffer.objects.get(slug=offer_slug)
    except Exception, e:
      raise exceptions.APIException(e.message)

    # Create client on user
    if not request.user.paymill_id:
      request.user.sync_paymill()

    # Create subscription with client & offer
    offer.create_subscription(request.POST.get('token'), request.user)

    # Return dummy status
    return response.Response({'payment' : True})
