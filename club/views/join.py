from django.views.generic import View
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from club.models import Club, ClubMembership
from coach.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD

class ClubList(ListView):
  model = Club
  template_name = 'club/join.html'
  context_object_name = 'clubs'

class ClubJoin(JsonResponseMixin, View, ):
  json_options = [JSON_OPTION_NO_HTML, ]

  def get(self, request, *args, **kwargs):
    # Check there is no existing relation
    club = get_object_or_404(Club, slug=kwargs['slug'])
    if club.has_user(request.user):
      raise Exception("Already in club")

    # Create new membership
    member = ClubMembership.objects.create(club=club, user=request.user, role='prospect')

    # Send notification to manager
    member.mail_club()

    self.json_options.append(JSON_OPTION_BODY_RELOAD)
    return self.render_to_response({})

