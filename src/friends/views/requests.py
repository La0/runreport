from django.views.generic import CreateView, DetailView, DeleteView
from friends.models import FriendRequest
from runreport.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE
from users.models import Athlete
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt


class FriendAdd(JsonResponseMixin, CreateView):
    model = FriendRequest
    fields = ('sender', 'recipient', )
    template_name = 'friends/_add.btn.html'

    @csrf_exempt  # needed for prod :(
    def dispatch(self, *args, **kwargs):
        return super(FriendAdd, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        # Save friend request
        fr = form.save()

        # Notify !
        fr.notify()

        return self.render_to_response({})

    def get_form_kwargs(self):
        if self.request.method != 'POST':
            raise Http404('Only POST')

        # Load requested friend
        recipient = get_object_or_404(
            Athlete, username=self.kwargs['username'])

        # Check not already in a FriendRequest
        if FriendRequest.objects.filter(
                sender=self.request.user, recipient=recipient).count() > 0:
            raise Http404('Already in a friend request')

        # Check not already a friend
        if recipient in self.request.user.friends.all():
            raise Http404('Already a friend')

        return {
            'data': {
                'sender': self.request.user.pk,
                'recipient': recipient.pk,
            },
        }


class FriendDelete(JsonResponseMixin, DeleteView):
    template_name = 'friends/delete.html'
    context_object_name = 'friend'

    def get_object(self):
        return self.request.user.friends.get(username=self.kwargs['username'])

    def delete(self, *args, **kwargs):
        # Do not delete the user
        # just remove the relation
        friend = self.get_object()
        self.request.user.friends.remove(friend)

        # Close
        self.json_options = [
            JSON_OPTION_CLOSE,
            JSON_OPTION_NO_HTML,
            JSON_OPTION_BODY_RELOAD,
        ]
        return super(FriendDelete, self).render_to_response({})


class FriendRequestChoice(JsonResponseMixin, DetailView):
    json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, ]

    def get_object(self):
        return get_object_or_404(
            FriendRequest, sender__username=self.kwargs['username'], recipient=self.request.user)

    def get_context_data(self, *args, **kwargs):
        if self.kwargs['action'] == 'refuse':
            self.object.delete()

        elif self.kwargs['action'] == 'accept':
            self.object.accept()

        else:
            raise Http404('Invalid action')

        return {}
