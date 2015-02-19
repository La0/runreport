from __future__ import absolute_import
from api.serializers import PlanSerializer, PlanSessionSerializer, PlanAppliedSerializer
from rest_framework import viewsets, views, response
from django.core.exceptions import PermissionDenied
from users.models import Athlete
from plan.tasks import publish_plan
from .mixins import PlanMixin

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

class PlanPublishView(PlanMixin, views.APIView):
  '''
  Publish a plan to a list of users
  '''
  def post(self, request, *args, **kwargs):
    self.load_plan()
    try:
      # Load requested athletes, trained by current user
      users = Athlete.objects.filter(memberships__trainers=self.request.user, pk__in=self.request.data['users'])
      if not users:
        raise Exception('No users to publish this plan.')
    except:
      raise PermissionDenied

    # Start task to publish the plan
    publish_plan.delay(self.plan, users)

    # Return dummy status
    return response.Response({'published' : True})

class PlanCopyView(PlanMixin, views.APIView):
  '''
  Copy a plan
  '''
  def post(self, request, *args, **kwargs):
    self.load_plan()
    self.plan.copy()

    # Return dummy status
    return response.Response({'copied' : True})

class PlanAppliedViewSet(PlanMixin, viewsets.ModelViewSet):
  '''
  Delete a plan application
  '''
  serializer_class = PlanAppliedSerializer

  def get_queryset(self):
    print 'boom queryset'
    self.load_plan()
    print 'loaded plan', self.plan
    return self.plan.applications.all()
