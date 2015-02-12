from api.serializers import AthleteSerializer, ClubMembershipSerializer
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView


class AthleteDetails(RetrieveAPIView):
  serializer_class = AthleteSerializer

  def get_object(self, *args, **kwargs):
    '''
    Always use current connected user
    '''
    return self.request.user


class ClubMembershipViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = ClubMembershipSerializer

  def get_queryset(self):
    # List all memberships as a trainer
    members = self.request.user.memberships.filter(role='trainer')
    return members
