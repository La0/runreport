from django.views.generic.edit import CreateView
from friends.models import FriendRequest
from coach.mixins import JsonResponseMixin
from users.models import Athlete
from django.shortcuts import get_object_or_404
from django.http import Http404

class FriendAdd(JsonResponseMixin, CreateView):
  model = FriendRequest
  template_name = 'friends/_add.btn.html'

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
    recipient = get_object_or_404(Athlete, username=self.kwargs['username'])

    # Check not already in a FriendRequest
    if FriendRequest.objects.filter(sender=self.request.user, recipient=recipient).count() > 0:
      raise Http404('Already in a friend request')

    # Check not already a friend
    if recipient in self.request.user.friends.all():
      raise Httpt404('Already a friend')

    return {
      'data' : {
        'sender' : self.request.user.pk,
        'recipient' : recipient.pk,
      },
    }
