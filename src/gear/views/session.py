from django.views.generic import UpdateView
from django.template.loader import render_to_string
from runreport.mixins import LoginRequired, JsonResponseMixin, JSON_OPTION_CLOSE
from sport.models import SportSession
from gear.forms import GearSessionForm


class GearSessionView(JsonResponseMixin, LoginRequired, UpdateView):
  '''
  Manage the gear from a session
  '''
  template_name = 'gear/session.html'
  form_class = GearSessionForm
  context_object_name = 'session'

  def get_queryset(self):
    # Only sessions from user
    return SportSession.objects.filter(day__week__user=self.request.user)

  def get_form_kwargs(self):
    out = super(GearSessionView, self).get_form_kwargs()
    out['user'] = self.request.user
    return out

  def form_valid(self, form):
    # Save gear in session
    session = form.save()

    # Close modal
    self.json_options = [JSON_OPTION_CLOSE, ]

    # Render list of gear items
    context = {
      'session' : session,
    }
    html = render_to_string('gear/_items.html', context)

    # Build json response
    return self.build_response(html=html, output='gear-%d' % session.pk )
