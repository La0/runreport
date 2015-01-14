from .mixins import ClubGroupMixin
from django.views.generic import ListView, CreateView, UpdateView


class ClubGroupList(ClubGroupMixin, ListView):
  context_object_name = 'groups'
  template_name = 'club/group/index.html'

class ClubGroupCreate(ClubGroupMixin, CreateView):
  template_name = 'club/group/edit.html'

class ClubGroupEdit(ClubGroupMixin, UpdateView):
  template_name = 'club/group/edit.html'
