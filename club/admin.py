from django.conf.urls import patterns, url
from django.shortcuts import get_object_or_404, render
from django.contrib import admin
from models import *
from payments.admin import PaymentTransactionInline

class ClubMembershipAdmin(admin.TabularInline):
  model = ClubMembership

class ClubLinkAdmin(admin.TabularInline):
  model = ClubLink

class ClubInviteAdmin(admin.ModelAdmin):
  list_display = ('recipient', 'slug', 'club', 'type', 'sender', 'created')

  def get_urls(self):
    # Add send view to admin urls
    urls = super(ClubInviteAdmin, self).get_urls()
    my_urls = patterns('',
      url(r'^(?P<invite_id>\d+)/send/?$', self.admin_site.admin_view(self.send_view), name="club-invite-send"),
    )
    return my_urls + urls

  def send_view(self, request, invite_id):
    '''
    Ask for a confirmation before sending
    '''
    invite = get_object_or_404(ClubInvite, pk=invite_id)
    if request.method == 'POST':
      invite.send()
    context = {
      'invite' : invite,
    }
    return render(request, 'club/send.html', context)

admin.site.register(ClubInvite, ClubInviteAdmin)

class ClubAdmin(admin.ModelAdmin):
  list_display = ('name', 'manager', '_has_full_access')
  inlines = []
  inlines = (
    PaymentTransactionInline,
    ClubMembershipAdmin,
    ClubLinkAdmin,
  )
admin.site.register(Club, ClubAdmin)
