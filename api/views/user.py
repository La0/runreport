from api.serializers import AthleteSerializer, ClubMembershipSerializer
from api.permissions import ClubPremiumPermission
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView


class AthleteDetails(RetrieveAPIView):
  serializer_class = AthleteSerializer
  permission_classes = (ClubPremiumPermission, )

  def get_object(self, *args, **kwargs):
    '''
    Always use current connected user
    '''
    return self.request.user


class ClubMembershipViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = ClubMembershipSerializer
  permission_classes = (ClubPremiumPermission, )

  def get_queryset(self):
    # List all memberships as a trainer
    # In a full access club
    members = self.request.user.memberships.filter(role='trainer')
    return [m for m in members if m.club.has_full_access]
