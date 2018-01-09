from django.views.generic import ListView


class FriendsHome(ListView):
    template_name = 'friends/home.html'
    context_object_name = 'friends'

    def get_queryset(self):
        friends = self.request.user.friends.all()
        friends = friends.order_by('first_name', 'last_name')
        return friends
