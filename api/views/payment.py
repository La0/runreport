from rest_framework import views, response, exceptions
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf import settings
from club.models import Club
from payments import get_api
from payments.account import RRAccount
from mangopaysdk.entities.cardregistration import CardRegistration
from mangopaysdk.entities.payin import PayIn
from mangopaysdk.tools.enums import CardType
from mangopaysdk.types.money import Money
from mangopaysdk.types.payinpaymentdetailscard import PayInPaymentDetailsCard
from mangopaysdk.types.payinexecutiondetailsdirect import PayInExecutionDetailsDirect
import logging

logger = logging.getLogger('payments')


class PaymentCardView(views.APIView):
  '''
  Finish card registration from a MangoPay transaction
  '''
  def post(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    try:

      # Load club
      club_slug = request.POST.get('club')
      club = Club.objects.get(slug=club_slug, manager=request.user)

      # Complete Card registration
      api = get_api()
      card_id = request.POST.get('card')
      if not card_id:
        cr = CardRegistration()
        cr.Id = request.POST.get('id')
        cr.RegistrationData = request.POST.get('data')
        cr_updated = api.cardRegistrations.Update(cr)
        card_id = cr_updated.CardId

      # Setup entry auth fee
      entry_fee = Money()
      entry_fee.Amount = settings.MANGOPAY_ENTRY_FEE * 100 # in cents
      entry_fee.Currency = 'EUR'

      # No auto fee here
      no_fee = Money()
      no_fee.Amount = 0
      no_fee.Currency = 'EUR'

      # Create an entry PayIn
      # to validate the card
      return_url = reverse('payment-3ds', args=(club.slug, card_id, club.build_card_hash(card_id)))
      rr = RRAccount() # receiver
      payin = PayIn()
      payin.PaymentType = 'CARD'
      payin.PaymentDetails = PayInPaymentDetailsCard()
      payin.PaymentDetails.CardType = CardType.CB_VISA_MASTERCARD
      payin.ExecutionDetails = PayInExecutionDetailsDirect()
      payin.ExecutionDetails.CardId = card_id
      payin.ExecutionDetails.SecureModeReturnURL = return_url
      payin.AuthorId = club.mangopay_id
      payin.CardId = card_id
      payin.CreditedUserId = rr.Id
      payin.CreditedWalletId = rr.wallet['Id']
      payin.DebitedFunds = entry_fee
      payin.Fees = no_fee
      payin.SecureMode = 'DEFAULT' # Use default (below 100 euros, no 3Ds)
      payin.SecureModeReturnURL = '%s%s' % (settings.MANGOPAY_RETURN_URL, return_url)
      resp = api.payIns.Create(payin)

      if resp.Status == 'SUCCEEDED':
        # Save the card id, not the pre-auth
        club.card_id = card_id
        club.save()

        out = {'card_saved' : True}

      elif resp.Status == 'CREATED':
        # Redirect user
        out = {'redirect' : resp.ExecutionDetails.SecureModeRedirectURL, }

      elif resp.Status == 'FAILED':
        # Raise error
        raise Exception(resp.ResultMessage)

    except Exception, e:
      logger.error('Card registration error for %s: %s' % (request.user, e))
      raise # TRASHME

      # Handle paymill errors
      raise exceptions.APIException(e)

    # Return dummy status
    return response.Response(out)
