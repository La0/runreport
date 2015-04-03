from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.gis import admin
from django.views.generic.base import RedirectView, TemplateView
from club.views import ClubInviteCheck

admin.autodiscover()

urlpatterns = patterns('',
  url(r'^/?', include('sport.urls')),
  url(r'^user/', include('users.urls')),
  url(r'^club/', include('club.urls')),
  url(r'^plan/', include('plan.urls')),
  url(r'^post/', include('post.urls')),
  url(r'^message/', include('messages.urls')),
  url(r'^track/', include('tracks.urls')),
  url(r'^friends/', include('friends.urls')),
  url(r'^(?P<type>help|news)/', include('page.urls')),

  # Invite
  url(r'^invite/(?P<slug>.*)', ClubInviteCheck.as_view(), name="club-invite"),

  # Landing pages
  url(r'^features/?', TemplateView.as_view(template_name='landing/features.html'), name="landing-features"),

  # Team
  url(r'^team/?', TemplateView.as_view(template_name='landing/team.html'), name="landing-team"),

  # Contact Form
  url(r'^contact/', include('contact_form.urls')),

  # Languages switch
  url(r'^lang/', include('django.conf.urls.i18n')),

  # API
  url(r'^api/v1/', include('api.urls', namespace='api')),
)

# Direct admin and static medias
dev_urls = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  (r'^medias/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# Hide a little admin
prod_urls = patterns('',
  url(r'^%s/' % settings.ADMIN_BASE_URL, include(admin.site.urls)),
  url(r'^admin/', RedirectView.as_view(url='http://docs.djangoproject.com/en/dev/ref/contrib/admin/')),
)

urlpatterns += settings.DEBUG and dev_urls or prod_urls

# Add static files in dev
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

