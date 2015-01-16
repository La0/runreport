from api.serializers import AthleteSerializer, PlanSerializer
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView


class AthleteDetails(RetrieveAPIView):
  serializer_class = AthleteSerializer

  def get_object(self, *args, **kwargs):
    '''
    Always use current connected user
    '''
    return self.request.user


class PlanViewSet(viewsets.ModelViewSet):
  serializer_class = PlanSerializer

  def get_queryset(self):
    return self.request.user.plans.all()
