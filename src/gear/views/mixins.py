from django.urls import reverse
from runreport.mixins import LoginRequired
from gear.forms import GearItemForm


class GearMixin(LoginRequired):
    '''
    Common mixin for gear management
    '''
    context_object_name = 'gear'
    form_class = GearItemForm

    def get_queryset(self):
        return self.request.user.items.all()

    def get_success_url(self):
        return reverse('gear')

    def get_form_kwargs(self):
        out = super(GearMixin, self).get_form_kwargs()
        out['user'] = self.request.user
        return out

    def form_valid(self, form):
        # Save with user
        gear = form.save(commit=False)
        gear.user = self.request.user
        gear.save()

        return super(GearMixin, self).form_valid(form)
