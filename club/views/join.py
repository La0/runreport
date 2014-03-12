from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from club.models import Club, ClubMembership
from coach.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD

class ClubList(ListView):
  model = Club
  template_name = 'club/join.html'
  context_object_name = 'clubs'

class ClubJoin(JsonResponseMixin, TemplateView, ):
  template_name = 'club/joined.html'

  def get_context_data(self, *args, **kwargs):
    context = {}

    # Check there is no existing relation
    club = get_object_or_404(Club, slug=kwargs['slug'])
    context['club'] = club
    if club.has_user(self.request.user):
      context['error'] = 'member'
      return context

    # Create new membership
    member = ClubMembership.objects.create(club=club, user=self.request.user, role='prospect')

    # Send notification to manager
    try:
      member.mail_club()
    except Exception, e:
      print 'Notification failed : %s' % (str(e), )
      # Don't keep membership when no mail is sent
      member.delete()
      context['error'] = 'mail'

    return context
