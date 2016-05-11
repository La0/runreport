from __future__ import absolute_import
from api.serializers import SportSerializer
from api.permissions import ClubPremiumPermission
from rest_framework import viewsets
from sport.models import Sport

class SportViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = SportSerializer
  queryset = Sport.objects.filter(depth=1).order_by('name')
  permission_classes = (ClubPremiumPermission, )
