from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.gis import admin
from django.views.generic.base import RedirectView, TemplateView
from club.views import ClubInviteCheck
from messages.views import ContactView
from runreport.views import FeaturesView, LegalView

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
  url(r'^premium/', include('payments.urls')),
  url(r'^badges/', include('badges.urls')),
  url(r'^equipment/', include('gear.urls')),
  url(r'^(?P<type>help|news)/', include('page.urls')),

  # Invite
  url(r'^invite/(?P<slug>.*)', ClubInviteCheck.as_view(), name="club-invite"),

  # Landing pages
  url(r'^features/athlete/?', TemplateView.as_view(template_name='landing/athlete.html'), name="features-athlete"),
  url(r'^features/trainer/?', TemplateView.as_view(template_name='landing/trainer.html'), name="features-trainer"),
  url(r'^features/?', FeaturesView.as_view(), name="features"),
  url(r'^legal/(?P<type>mentions|cgu)/?', LegalView.as_view(), name="legal"),

  # Contact Form
  url(r'^contact/(?P<sent>sent)?', ContactView.as_view(), name='contact'),

  # Languages switch
  url(r'^lang/', include('django.conf.urls.i18n')),

  # API
  url(r'^api/v1/', include('api.urls', namespace='api')),
)

# Direct admin and static medias
dev_urls = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  (r'^medias/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Hide a little admin
prod_urls = patterns('',
  url(r'^%s/' % settings.ADMIN_BASE_URL, include(admin.site.urls)),
  url(r'^admin/', RedirectView.as_view(url='http://docs.djangoproject.com/en/dev/ref/contrib/admin/', permanent=True)),
)

urlpatterns += settings.DEBUG and dev_urls or prod_urls

