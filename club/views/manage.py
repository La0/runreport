from mixins import ClubManagerMixin
from django.views.generic import DetailView
from club.models import Club

class ClubManage(ClubManagerMixin, DetailView):
  model = Club
  template_name = "club/manage.html"
