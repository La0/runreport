from club.models import ClubInvite
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.http import Http404
from mixins import ClubInviteMixin, ClubManagerMixin
from club.forms import ClubInviteForm

class ClubInviteCheck(DetailView):
  template_name = 'club/invite.html'
  model = ClubInvite
  context_object_name = 'invite'

  def get_context_data(self, *args, **kwargs):
    # Check private invite is not already used
    if self.object.private and self.object.used:
      raise Http404("Invite used.")

    # Save invite in session
    self.request.session['invite'] = self.object.slug

    context = super(ClubInviteCheck, self).get_context_data(*args, **kwargs)
    return context

class ClubInviteApply(ClubInviteMixin, TemplateView):
  template_name = 'club/invite_apply.html'

  def get_context_data(self, *args, **kwargs):
    # Only apply athlete & trainer
    if not self.invite.type in ('trainer', 'athlete'):
      raise Http404('Unsupported invite type')

    # Apply !
    self.invite.apply(self.request.user)

    context = super(ClubInviteApply, self).get_context_data(*args, **kwargs)
    context['invite'] = self.invite
    return context

class ClubInviteAdd(ClubManagerMixin, CreateView):
  template_name = 'club/invite_add.html'
  model = ClubInvite
  form_class = ClubInviteForm

  def form_valid(self, form, *args, **kwargs):
    invite = form.save(commit=False)
    invite.club = self.club
    invite.sender = self.request.user
    invite.save()
    return self.render_to_response(self.get_context_data({'invite': invite}))
