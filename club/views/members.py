from django.views.generic import ListView, DetailView
from club.models import Club
from django.shortcuts import get_object_or_404

class ClubMembers(ListView):
  template_name = 'club/members.html'
  context_object_name = 'members'
  
  def get_queryset(self):
    self.club = get_object_or_404(Club, slug=self.kwargs['slug'])
    return self.club.members.all().order_by('first_name')

  def get_context_data(self, **kwargs):
    context = super(ClubMembers, self).get_context_data(**kwargs)
    context['club'] = self.club
    return context

class ClubMember(DetailView):
  template_name = 'club/member.html'
  context_object_name = 'member'
  
  def get_object(self):
    self.club = get_object_or_404(Club, slug=self.kwargs['slug'])
    return self.club.members.get(username=self.kwargs['username'])

  def get_context_data(self, **kwargs):
    context = super(ClubMember, self).get_context_data(**kwargs)
    context['club'] = self.club
    return context

