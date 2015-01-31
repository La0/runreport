from api.serializers import AthleteSerializer, PlanSerializer, PlanSessionSerializer, SportSerializer, ClubMembershipSerializer
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from sport.models import Sport


class AthleteDetails(RetrieveAPIView):
  serializer_class = AthleteSerializer

  def get_object(self, *args, **kwargs):
    '''
    Always use current connected user
    '''
    return self.request.user

class SportViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = SportSerializer
  queryset = Sport.objects.filter(depth=1).order_by('name')


class PlanViewSet(viewsets.ModelViewSet):
  serializer_class = PlanSerializer

  def get_queryset(self):
    return self.request.user.plans.all()

class PlanSessionViewSet(viewsets.ModelViewSet):
  serializer_class = PlanSessionSerializer

  def get_plan(self):
    return self.request.user.plans.get(pk=self.kwargs['plan_pk'])

  def get_queryset(self):
    return self.get_plan().sessions.all()

class ClubMembershipViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = ClubMembershipSerializer

  def get_queryset(self):
    # List all memberships as a trainer
    members = self.request.user.memberships.filter(role='trainer')
    return members

