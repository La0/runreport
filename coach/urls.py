from coffin.conf.urls import *
from coach.settings import MEDIA_ROOT, DEBUG, ADMIN_BASE_URL
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView
from club.views import ClubInviteCheck

admin.autodiscover()

urlpatterns = patterns('',
  url(r'^/?', include('run.urls')),
  url(r'^user/', include('users.urls')),
  url(r'^club/', include('club.urls')),
  url(r'^plan/', include('plan.urls')),
  url(r'^(?P<type>help|news)/', include('page.urls')),

  # Invite
  url(r'^invite/(?P<slug>.*)', ClubInviteCheck.as_view(), name="club-invite"),

  # Landing pages
  url(r'^features/?', TemplateView.as_view(template_name='landing/features.html'), name="landing-features"),

  # Contact Form
  url(r'^contact/', include('contact_form.urls')),
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
