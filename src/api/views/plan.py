from __future__ import absolute_import
from django.db.models import Max
from api.serializers import PlanSerializer, PlanSessionSerializer, PlanAppliedSerializer, MessageSerializer
from rest_framework import viewsets, views, response
from django.core.exceptions import PermissionDenied
from users.models import Athlete
from plan.tasks import publish_plan
from .mixins import PlanMixin, PlanSessionMixin
from messages.models import Conversation, TYPE_PLAN_SESSION


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer

    def get_queryset(self):
        plans = self.request.user.plans.all()
        plans = plans.prefetch_related('applications', 'sessions')
        plans = plans.annotate(nb_weeks=Max('sessions__week'))
        plans = plans.order_by('-updated', 'name')
        return plans


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
            users = Athlete.objects.filter(
                memberships__trainers=self.request.user, pk__in=self.request.data['users'])
            if not users:
                raise Exception('No users to publish this plan.')
        except BaseException:
            raise PermissionDenied

        # Start task to publish the plan
        publish_plan.delay(self.plan.pk, users.values_list('pk', flat=True))

        # Return dummy status
        return response.Response({'published': True})


class PlanCopyView(PlanMixin, views.APIView):
    '''
    Copy a plan
    '''

    def post(self, request, *args, **kwargs):
        self.load_plan()
        self.plan.copy()

        # Return dummy status
        return response.Response({'copied': True})


class PlanAppliedViewSet(PlanMixin, viewsets.ModelViewSet):
    '''
    Delete a plan application
    '''
    serializer_class = PlanAppliedSerializer

    def get_queryset(self):
        self.load_plan()
        return self.plan.applications.all()


class PlanMessagesViewSet(PlanSessionMixin, viewsets.ModelViewSet):
    '''
    Manages messages in a plan (future private comments)
    '''
    serializer_class = MessageSerializer

    def get_queryset(self):
        self.load_session()
        if self.session.comments is None:
            return []
        return self.session.comments.messages.all()

    def create(self, request, *args, **kwargs):
        # Create conversation if it does not exists
        self.load_session()
        if self.session.comments is None:
            self.session.comments = Conversation.objects.create(
                type=TYPE_PLAN_SESSION, )
            self.session.save()

        # Continue normal creation
        return super(PlanMessagesViewSet, self).create(
            request, *args, **kwargs)
