from club.models import Club, ClubMembership, ClubInvite
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.core.urlresolvers import reverse
from club.forms import ClubGroupForm

class ClubMixin(object):
  """
  View mixin which verifies that:
    * loads a club from slug kwargs
    * check the logged in user is a club trainer
    * or an admin
  """
  roles_allowed = (
    'trainer',
    'staff',
  )
  role = None # Role of the visitor

  def check(self, request, *args, **kwargs):
    # Load club
    self.club = get_object_or_404(Club, slug=kwargs['slug'])

    if not request.user.is_authenticated():
      self.check_public()

    # Check we have a trainer or an admin or a staff member
    if not request.user.is_staff:
      try:
        m = request.user.memberships.get(club=self.club, role__in=self.roles_allowed)
        self.role = m.role
      except:
        self.check_public()

    # Load members
    self.member = None
    if 'username' in kwargs:
      self.membership = ClubMembership.objects.get(user__username=kwargs['username'], club=self.club)
      self.member = self.membership.user

  def check_public(self):
    # Special case for public pages (members list)
    # on public clubs
    if not self.club.private and 'public' in self.roles_allowed:
      self.role = 'public'
    else:
      raise PermissionDenied

  def dispatch(self, request, *args, **kwargs):
    self.check(request, *args, **kwargs)
    return super(ClubMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(ClubMixin, self).get_context_data(**kwargs)
    context['club'] = self.club
    context['member'] = self.member
    context['role'] = self.role
    return context

class ClubManagerMixin(ClubMixin):
  """
  Previous mixin, but user must be:
    * the manager of the club
    * or is a super user
  """
  def dispatch(self, request, *args, **kwargs):
    self.check(request, *args, **kwargs)
    if not request.user.is_staff and self.club.manager != request.user:
      raise PermissionDenied
    return super(ClubManagerMixin, self).dispatch(request, *args, **kwargs)

class ClubCreateMixin(object):
  """
  Check that the user is:
    * logged in
    * does not already manage a club
    * has a loaded invite in session
  """
  invite = None

  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    if Club.objects.filter(manager=request.user).count() > 0:
      raise PermissionDenied

    try:
      invite_slug = request.session['invite']
      self.invite = ClubInvite.objects.get(slug=invite_slug)
    except:
      raise Http404('Invalid or missing Beta invitation.')

    return super(ClubCreateMixin, self).dispatch(request, *args, **kwargs)

class ClubGroupMixin(object):
  form_class = ClubGroupForm
  context_object_name = 'group'
  public = False # anyone can access ?
  editable = True # editable version ?

  # Models instances
  club = None
  group = None


  def get_queryset(self):
    if self.editable:
      return self.request.user.groups_owned.all()
    return self.club.groups.all()

  def get_object(self):
    return self.get_queryset().get(slug=self.kwargs['group_slug'])

  def dispatch(self, request, *args, **kwargs):
    '''
    Check user is:
     * logged in
     * is staff or trainer of the club
    '''
    if not self.request.user.is_authenticated:
      raise PermissionDenied

    # Load club
    self.club = Club.objects.get(slug=self.kwargs['slug'])

    # Check user role in club
    if not self.request.user.is_staff:
      try:
        self.club.clubmembership_set.get(user=self.request.user, role__in=('trainer', 'staff'))
      except:
        if self.public:
          self.editable = False
        else:
          raise PermissionDenied

    # Load group
    if 'group_slug' in self.kwargs:
      self.group = self.club.groups.get(slug=self.kwargs['group_slug'])

    return super(ClubGroupMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, *args, **kwargs):
    context = super(ClubGroupMixin, self).get_context_data(*args, **kwargs)
    context['club'] = self.club
    context['group'] = self.group
    context['editable'] = self.editable
    return context

  def get_success_url(self):
    # go to edition
    return reverse('club-group-edit', args=(self.club.slug, self.group.slug, ))

  def form_valid(self, form):
    # Setup owner & club
    self.group = form.save(commit=False)
    if not hasattr(self.group, 'creator'):
      self.group.creator = self.request.user
    self.group.club = self.club
    self.group.save()

    return super(ClubGroupMixin, self).form_valid(form)
