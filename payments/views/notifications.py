from django.views.generic import View
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from mangopaysdk.types.dto import Dto
from payments import get_notification_hash, get_api
from payments.models import PaymentTransaction
from club.models import Club
import json

class PaymentNotification(View):
  '''
  Mangopay notification endpoint
  '''

  def get(self, *args, **kwargs):
    '''
    Parameters are :
     * Date: 1445531755
     * EventType: PAYIN_NORMAL_SUCCEEDED
     * RessourceId: 9095865
    '''
    # Get resource id
    resource_id = self.request.GET.get('RessourceId')
    if not resource_id:
      raise Exception('Missing Resource Id')

    # Check hash
    event_type = self.request.GET.get('EventType')
    if not event_type:
      raise Exception('Missing Event Type')
    h = get_notification_hash(event_type)
    if self.kwargs.get('hash') != h:
      raise PermissionDenied

    # Detect type & status
    api = get_api()
    category, level, state = event_type.split('_')
    if category == 'PAYIN' and level == 'NORMAL':
      # Load payin
      resp = api.payIns.Get(resource_id)

      # Get club
      club = Club.objects.get(mangopay_id=resp.AuthorId)

      # Get (optional) period
      try:
        period = club.periods.get(mangopay_id=resp.Id)
      except:
        period = club.current_period

    else:
      raise Exception('Unsupported notification type %s' % event_type)


    # Format resp as full dict
    def __fmt(x):
      return dict([(k, isinstance(v, Dto) and __fmt(v) or v) for k,v in x.__dict__.items()])
    resp_dict = __fmt(resp)

    # Save as Transaction
    defaults = {
      'response' : json.dumps(resp_dict),
      'status': state,
      'period' : period,
    }
    transaction, created = PaymentTransaction.objects.get_or_create(club=club, mangopay_id=resource_id, defaults=defaults)
    if not created:
      if transaction.status != state and state != 'CREATED':
        transaction.status = state
      transaction.period = period
      transaction.response = defaults['response']
      transaction.save()

    # Return empty response !
    return HttpResponse('', status=200)
