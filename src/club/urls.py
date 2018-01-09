from django.conf.urls import url, include
from club.views import *

user_patterns = [
    url(r'^role/?',
        ClubMemberRole.as_view(),
        name="club-member-role"),
    url(r'^trainers/?',
        ClubMemberTrainers.as_view(),
        name="club-member-trainers"),
    url(r'^races/?',
        ClubMemberRaces.as_view(),
        name="club-member-races"),
]

club_patterns = [
    # Places, from events
    url(r'^/places/', include('events.urls')),

    # Manager
    url(r'^/races/?$', ClubRaces.as_view(), name="club-races"),
    url(r'^/manage/?$', ClubManage.as_view(),
        name="club-manage"),
    url(r'^/link/add/?$', ClubLinkAdd.as_view(),
        name="club-link-add"),
    url(r'^/link/delete/(?P<id>\d+)?$',
        ClubLinkDelete.as_view(),
        name="club-link-delete"),

    # Join
    url(r'^/join/?$', ClubJoin.as_view(), name="club-join"),
    url(r'^/join/(?P<secret>[\w]+)/?$',
        ClubJoin.as_view(),
        name="club-join-private"),

    # Member
    url(r'^/(?P<username>[\w\_]+)/',
        include(user_patterns)),

    # Members
    url(r'^/(?P<type>[\w]+)-by-(?P<sort>[\w-]+)/?$',
        ClubMembers.as_view(), name="club-members-name"),
    url(r'^/trainer/(?P<username>[\w_]+)/?$',
        ClubMembers.as_view(),
        {'type': 'trainer',
         },
        name="club-trainer",
        ),
    url(r'^/no-trainer/?$', ClubMembers.as_view(),
        {'type': 'notrainer', }, name="club-no-trainer", ),
    url(r'^/by-(?P<sort>[\w-]+)/?$',
        ClubMembers.as_view(),
        name="club-members-sort"),
    url(r'^/?$', ClubMembers.as_view(), name="club-members"),

    # Members export
    url(r'^/export/?$',
        ClubMembersExport.as_view(),
        name="club-members-export"),

    # Subscriptions
    url(r'^/subscriptions/add/?$',
        ClubSubscriptionsAdd.as_view(),
        name="club-subscriptions-add"),
    url(r'^/subscriptions/upload/?$',
        ClubSubscriptionsUpload.as_view(),
        name="club-subscriptions-upload"),
    url(r'^/subscriptions/(?P<csv_name>[\w]+)/?$',
        ClubSubscriptionsEditor.as_view(),
        name="club-subscriptions-editor"),

    # Groups
    url(r'^/group/new/?',
        ClubGroupCreate.as_view(),
        name="club-group-create"),
    url(r'^/group/(?P<group_slug>[\w\-\_]+)/members/?',
        ClubGroupMembers.as_view(),
        name="club-group-members"),
    url(r'^/group/(?P<group_slug>[\w\-\_]+)/edit/?',
        ClubGroupEdit.as_view(), name="club-group-edit"),
    url(r'^/group/(?P<group_slug>[\w\-\_]+)/delete/?',
        ClubGroupDelete.as_view(), name="club-group-delete"),
    url(r'^/group/(?P<group_slug>[\w\-\_]+)/?',
        ClubGroupView.as_view(), name="club-group"),
    url(r'^/group/?',
        ClubGroupList.as_view(),
        name="club-groups"),
]

urlpatterns = [
    # Create
    url(r'^create/?$', ClubCreate.as_view(), name="club-create"),

    # List to Join
    url(r'^join/?$', ClubList.as_view(), name="club-list"),

    # List for admins
    url(r'^admin/?$',
        ClubAdminListView.as_view(),
        name="club-admin-list"),

    # With an existing club
    url(r'^(?P<slug>[\w\_\-]+)', include(club_patterns)),

    # Landing page
    url(r'^/?', ClubInviteAsk.as_view(), name="club-landing"),
]
