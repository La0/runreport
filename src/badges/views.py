from django.views.generic import ListView
from django.core.exceptions import PermissionDenied


class BadgesView(ListView):
    '''
    List all the badges for a user
    By default, currently logged in user
    '''
    template_name = 'badges/list.html'
    context_object_name = 'badges'

    def get_user(self):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        return self.request.user

    def get_context_data(self):
        context = super(BadgesView, self).get_context_data()
        context['member'] = self.request.user
        return context

    def get_queryset(self):
        # All badges for current user
        user = self.get_user()
        badges = user.badges.all()

        # Sort by categories
        cats = set(badges.values_list('category__name', flat=True))
        return dict([(c, badges.filter(category__name=c)) for c in cats])
