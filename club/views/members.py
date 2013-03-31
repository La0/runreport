from django.views.generic import ListView, DetailView
from mixins import ClubMixin

class ClubMembers(ClubMixin, ListView):
  template_name = 'club/members.html'
  context_object_name = 'members'
  
  def get_queryset(self):
    return self.club.members.all().order_by('first_name')

class ClubMember(ClubMixin, DetailView):
  template_name = 'club/member.html'
  context_object_name = 'member'
  
  def get_object(self):
    return self.club.members.get(username=self.kwargs['username'])
