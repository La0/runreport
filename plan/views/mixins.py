from django.core.exceptions import PermissionDenied
from plan.models import *
from django.http import Http404
from django.shortcuts import get_object_or_404

class PlanMixin(object):
  """
  View mixin which verifies that:
    * check the logged in user is a club trainer
    * or an admin
  """
  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    # Load memberships:
    # * only the club where they train for trainers
    # * the admin club where he is a member
    members = request.user.memberships
    if not request.user.is_staff:
      members = members.filter(role="trainer")
    if not members:
      raise PermissionDenied
    self.clubs = [m.club for m in members.all()]

    # Check club if needed
    self.club = None
    if 'club' in kwargs:
      clubs_filtered = [c for c in self.clubs if c.slug == kwargs['club']]
      if not clubs_filtered:
        raise Http404('Club not found')
      self.club = clubs_filtered.pop()

    # Load optional plan (using slug kwargs)
    self.plan = None
    if 'slug' in kwargs:
      try:
        self.plan = Plan.objects.get(slug=kwargs['slug'], creator=request.user)
      except Exception, e:
        raise Http404('Plan not found')

    # Load optional week
    self.plan_week = None
    if self.plan is not None and 'week' in kwargs:
      try:
        self.plan_week = PlanWeek.objects.get(plan=self.plan, order=kwargs['week'])
      except Exception, e:
        pass

    # Load optional session 
    self.plan_session = None
    if self.plan_week is not None and 'day' in kwargs:
      try:
        self.plan_session = PlanSession.objects.get(week=self.plan_week, day=kwargs['day'])
      except Exception, e:
        pass

    return super(PlanMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(PlanMixin, self).get_context_data(**kwargs)
    context['clubs'] = self.clubs
    context['club'] = self.club
    context['plan'] = self.plan
    context['week'] = self.plan_week
    context['session'] = self.plan_session
    return context

  def get_object(self):
    return self.plan

class PlanUserMixin(object):
  '''
  Check that the user can simply view the details of a plan
  applied to his training
  '''
  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    # Get a plan for this creator / slug
    self.plan = get_object_or_404(Plan, slug=kwargs['slug'], creator__username=kwargs['creator'])

    # Check the user is authorized to view it
    if not PlanUsage.objects.filter(plan=self.plan, user=request.user).count():
      raise PermissionDenied

    return super(PlanUserMixin, self).dispatch(request, *args, **kwargs)

  def get_object(self):
    return self.plan

  def get_context_data(self, **kwargs):
    context = super(PlanUserMixin, self).get_context_data(**kwargs)
    context['plan'] = self.plan
    return context

