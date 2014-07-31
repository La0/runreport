from django.views.generic.edit import UpdateView
from users.forms import GarminForm
from users.models import Athlete
from sport.models import GarminActivity
from django.db.models import Max
from django.core.urlresolvers import reverse

class GarminLogin(UpdateView):
  template_name = 'users/garmin.html'
  form_class = GarminForm
  model = Athlete

  def get_object(self):
    return self.request.user

  def form_valid(self, form, *args, **kwargs):
    form.save()
    ctx = {
      'form' : form,
      'connected' : True,
    }
    return self.render_to_response(self.get_context_data(**ctx))

  def get_context_data(self, *args, **kwargs):
    context = super(GarminLogin, self).get_context_data(*args, **kwargs)

    # Imported Activities
    activities = GarminActivity.objects.filter(user=self.request.user)
    context['activities_nb'] = activities.count()
    context['activities_dates'] = activities.aggregate(created=Max('created'), updated=Max('updated'))

    return context
