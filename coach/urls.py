from coffin.conf.urls import *
from coach.settings import MEDIA_ROOT, DEBUG, ADMIN_BASE_URL
from django.contrib import admin
from django.views.generic.base import RedirectView
from club.views import ClubInviteCheck, ClubInviteApply
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^/?', include('run.urls')),
  url(r'^user/', include('users.urls')),
  url(r'^club/', include('club.urls')),
  url(r'^(?P<type>help|news)/', include('page.urls')),

  # Invite
  url(r'^invite/apply/?$', ClubInviteApply.as_view(), name="club-invite-apply"),
  url(r'^invite/(?P<slug>.*)', ClubInviteCheck.as_view(), name="club-invite"),
)

# Direct admin and static medias
dev_urls = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  (r'^medias/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)

# Hide a little admin
prod_urls = patterns('',
  url(r'^%s/' % ADMIN_BASE_URL, include(admin.site.urls)),
  url(r'^admin/', RedirectView.as_view(url='http://docs.djangoproject.com/en/dev/ref/contrib/admin/')),
)

urlpatterns += DEBUG and dev_urls or prod_urls
