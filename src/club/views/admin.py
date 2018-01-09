from django.views.generic import ListView
from club.views.mixins import AdminMixin
from club.models import Club


class ClubAdminListView(AdminMixin, ListView):
    template_name = 'club/admin.html'
    context_object_name = 'clubs'
    queryset = Club.objects.order_by('name')
