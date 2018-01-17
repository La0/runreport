from club.models import ClubInvite
from django.shortcuts import get_object_or_404
from users.models import Athlete, PRIVACY_LEVELS
from django.core.exceptions import PermissionDenied
from club import ROLES


class UserInviteMixin(object):
    invite = None

    def dispatch(self, *args, **kwargs):
        self.check_invite()  # Load invite first
        out = super(UserInviteMixin, self).dispatch(*args, **kwargs)
        return out

    def get_context_data(self, *args, **kwargs):
        context = super(UserInviteMixin, self).get_context_data(*args, **kwargs)

        # Add invite if any
        if self.invite:
            context['invite'] = self.invite

        return context

    def check_invite(self):
        # Load a potential invite from session
        try:
            self.invite = ClubInvite.objects.get(
                slug=self.request.session['invite'])
        except BaseException:
            return False
        return True


class ProfilePrivacyMixin(object):
    '''
    Check the user has any right to view a public profile
    Loads available rights according to context
    '''
    member = None
    privacy = []  # Rights available to visitor
    rights_needed = ()  # Needed rights to access the page

    def get_member(self):
        '''
        Load the requested athlete
        Check privacy rights
        '''
        self.member = get_object_or_404(
            Athlete, username=self.kwargs['username'])

        # Load privacy rights
        self.privacy = self.member.get_privacy_rights(self.request.user)

        # Check basic access
        for right in self.rights_needed:
            if right not in self.privacy:
                raise PermissionDenied

        return self.member

    def get_user(self):
        # Alias on get_member for sport mixins
        return self.member or self.get_member()

    def dispatch(self, *args, **kwargs):
        # Check you have the rights
        self.get_member()

        return super(ProfilePrivacyMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(
            ProfilePrivacyMixin,
            self).get_context_data(
            *
            args,
            **kwargs)
        context['member'] = self.member
        context['privacy'] = self.privacy
        context['levels'] = dict(PRIVACY_LEVELS)
        context['roles'] = dict(ROLES)
        return context
