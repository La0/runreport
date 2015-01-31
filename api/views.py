from api.serializers import AthleteSerializer, PlanSerializer, PlanSessionSerializer, SportSerializer, ClubMembershipSerializer
from rest_framework import viewsets, views, response
from rest_framework.generics import RetrieveAPIView
from sport.models import Sport
from django.core.exceptions import PermissionDenied
from users.models import Athlete
from plan.tasks import publish_plan


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

class PlanPublishView(views.APIView):
  '''
  Publish a plan to a list of users
  '''
  def post(self, request, pk):
    try:
      # Load plan
      plan = self.request.user.plans.get(pk=pk)

      # Load requested athletes, trained by current user
      users = Athlete.objects.filter(memberships__trainers=self.request.user, pk__in=self.request.data['users'])
      if not users:
        raise Exception('No users to publish this plan.')
    except:
      raise PermissionDenied

    # Start task to publish the plan
    publish_plan.delay(plan, users)

    # Return dummy status
    return response.Response({'published' : True})

class ClubMembershipViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = ClubMembershipSerializer

  def get_queryset(self):
    # List all memberships as a trainer
    members = self.request.user.memberships.filter(role='trainer')
    return members
