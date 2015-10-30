from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.conf import settings
from club.views.mixins import ClubManagerMixin
from payments import get_api
from mangopaysdk.entities.cardregistration import CardRegistration
from datetime import date

class PaymentCardView(ClubManagerMixin, TemplateView):
  '''
  Add a card to a club
  '''
  template_name = 'payments/card.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PaymentCardView, self).get_context_data(*args, **kwargs)

    # Add months & years for form
    context['months'] = [str(m).zfill(2) for m in range(1, 13)]
    today = date.today()
    context['years'] = range(today.year, today.year+13)

    # Add card registration process
    context['registration'] = None
    context['mangopay_id'] = settings.MANGOPAY_ID
    api = get_api()

    # Need a mangopay user id
    if not self.club.mangopay_id:
      self.club.sync_mangopay()

    # Card registration
    cr = CardRegistration()
    cr.UserId = self.club.mangopay_id
    cr.Currency = 'EUR'
    context['registration'] = api.cardRegistrations.Create(cr)

    return context

class Payment3DsView(ClubManagerMixin, TemplateView):
  '''
  Handle 3D secure returning user
  '''
  template_name = 'payments/3ds.html'

  def dispatch(self, *args, **kwargs):
    out = super(Payment3DsView, self).dispatch(*args, **kwargs)

    # Check the hash
    card_id = self.kwargs.get('card_id')
    h = self.club.build_card_hash(card_id)
    if self.kwargs.get('hash') != h:
      raise PermissionDenied

    # Save card, when not set or different
    if not self.club.card_id or card_id != self.club.card_id:
      self.club.card_id = card_id
      self.club.save()

    return out
