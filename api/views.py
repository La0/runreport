from api.serializers import AthleteSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from rest_framework.generics import RetrieveAPIView


class AthleteDetails(RetrieveAPIView):
  serializer_class = AthleteSerializer

  def get_object(self, *args, **kwargs):
    '''
    Always use current connected user
    '''
    return self.request.user
