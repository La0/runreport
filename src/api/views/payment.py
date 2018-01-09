from rest_framework import views, response, exceptions
from django.core.exceptions import PermissionDenied
from django.conf import settings
from club.models import Club
from payments import get_api
from mangopaysdk.entities.cardregistration import CardRegistration
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

            # Create PayIn
            # to validate the card
            resp = club.init_payment(settings.MANGOPAY_ENTRY_FEE, card_id)

            if resp.Status == 'SUCCEEDED':
                # Save the card id, not the pre-auth
                club.card_id = card_id
                club.save()

                out = {'card_saved': True}

            elif resp.Status == 'CREATED':
                # Redirect user
                out = {'redirect': resp.ExecutionDetails.SecureModeRedirectURL, }

            elif resp.Status == 'FAILED':
                # Raise error
                raise Exception(resp.ResultMessage)

        except Exception as e:
            logger.error('Card registration error for %s: %s' %
                         (request.user, e))
            raise  # TRASHME

            # Handle paymill errors
            raise exceptions.APIException(e)

        # Return dummy status
        return response.Response(out)
