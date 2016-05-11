from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from .mixins import GearMixin


class GearListView(GearMixin, ListView):
  '''
  List all the gear from a user
  '''
  context_object_name = 'gears'
  template_name = 'gear/list.html'


class GearCreateView(GearMixin, CreateView):
  '''
  Create a gear item from a user
  '''
  template_name = 'gear/edit.html'


class GearEditView(GearMixin, UpdateView):
  '''
  Edit a gear item from a user
  '''
  template_name = 'gear/edit.html'


class GearDeleteView(GearMixin, DeleteView):
  '''
  Delete a gear item from a user
  '''
  template_name = 'gear/delete.html'
