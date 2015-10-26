from django.views.generic import DetailView
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from mixins import ClubManagerMixin
from club.models import ClubMembership
from club.forms import ClubMembershipForm
from club import ROLES
from club.tasks import mail_member_role
from payments.bill import Bill
from runreport.mixins import JsonResponseMixin, JSON_STATUS_ERROR, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE

import logging
logger = logging.getLogger('club')

class ClubMemberRole(JsonResponseMixin, ClubManagerMixin, ModelFormMixin, ProcessFormView, DetailView):
  template_name = 'club/role.html'
  context_object_name = 'membership'
  model = ClubMembership
  form_class = ClubMembershipForm

  def get_roles(self):
    '''
    List roles usable for switchs
    '''
    # No role change for club manager
    if self.club.manager == self.member:
        return {}

    from collections import OrderedDict
    roles = OrderedDict(ROLES)

    # Remove prospect (can't go back there)
    roles.pop('prospect')

    # Only manager can archive
    if self.club.manager != self.request.user:
      roles.pop('archive')

    # Remove current role
    if self.membership.role in roles:
      roles.pop(self.membership.role)

    return roles

  def get_context_data(self, **kwargs):
    context = super(ClubMemberRole, self).get_context_data(**kwargs)
    context['membership'] = self.membership
    context['member'] = self.member
    context['roles'] = self.get_roles()

    # Add bill manager for club
    bill = Bill(self.club)
    bill.calc()
    context['bill'] = bill
    return context

  def get_form(self, form_class):
    self.role_original = self.membership.role
    # Load object before form init
    if not hasattr(self, 'object'):
      self.get_object()
    return super(ClubMemberRole, self).get_form(form_class)

  def form_valid(self, form):
    if self.request.user.demo:
      raise Exception("No edit for demo")

    try:
      membership = form.save(commit=False)
      membership.trainers = form.cleaned_data['trainers'] # Weird :/

      # Special case for deletion of prospect
      if membership.role == 'archive' and self.role_original == 'prospect':

        # Send email
        if form.cleaned_data['send_mail']:
          mail_member_role.delay(membership, self.role_original)

        # Delete
        membership.delete()

        # Close & reload parent
        self.json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE, ]
        return self.render_to_response({})

      # Delete or save
      if 'delete' in self.request.POST:
        membership.delete()
        self.json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE, ]
      else:
        membership.save()

      if self.role_original != membership.role:
        # When losing trainer role
        # remove all athletes
        if self.role_original == 'trainer':
          membership.user.trainees.clear()

        # Only send mail for new roles
        # When send_mail is valid
        if form.cleaned_data['send_mail']:
          mail_member_role.delay(membership, self.role_original)

        # Reload page for roles updates
        # When some trainers are specified
        if not (membership.role == 'athlete' and membership.trainers.count() == 0):
          self.json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE, ]

    except Exception, e:
      logger.error('Failed to save role update for %s : %s' % (membership.user, str(e)))
      raise Exception("Failed to save")

    return self.render_to_response(self.get_context_data(**{'form' : form, 'saved': True}))

  def form_invalid(self, form):
    self.json_status = JSON_STATUS_ERROR
    return self.render_to_response(self.get_context_data(**{'form' : form}))

  def get_object(self):
    self.object = self.membership # needed for inherited classes
    return self.object