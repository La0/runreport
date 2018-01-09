from django.views.generic import ListView, View
from django.utils.translation import ugettext as _
from django.http import Http404
from mixins import ClubMixin
from users.models import Athlete
from django.db.models import Count, Max
from datetime import date, timedelta, MINYEAR
from runreport.mixins import CsvResponseMixin

import logging
logger = logging.getLogger('club')


class ClubMembers(ClubMixin, ListView):
    template_name = 'club/members.html'
    model = Athlete

    # A club athlete has access too
    roles_allowed = ('staff', 'trainer', 'athlete', 'public')

    def load_members(self):
        # Filter members
        default_type = 'athletes'
        filters = {
            'all': {
                'memberships__role__in': ('athlete', 'trainer', 'staff'),
            },
            'athletes': {
                'memberships__role__in': ('athlete', 'trainer'),
                'memberships__trainers': self.request.user,
            },
            'staff': {
                'memberships__role': 'staff',
            },
            'prospects': {
                'memberships__role': 'prospect',
            },
            'trainer': {
                'memberships__role__in': ('athlete', 'trainer'),
                'memberships__trainers__username': self.kwargs.get('username', None),
            },
            'notrainer': {
                'memberships__role__in': ('athlete', 'trainer'),
                'memberships__trainers__isnull': True,
            },
            'archives': {
                'memberships__role': 'archive',
            }
        }

        # Remove filters for non manager
        if self.request.user != self.club.manager and not self.request.user.is_staff:
            del filters['all']
            del filters['staff']
            del filters['prospects']
            del filters['archives']
            del filters['trainer']

        # Load members, sorted by name
        asked_type = self.kwargs.get('type', default_type)
        if asked_type not in filters:
            # Fallback to simplified members
            self.template_name = 'club/members.athletes.html'
            return self.load_simplified_members()

        f = filters[asked_type]
        members = self.club.members.prefetch_related(
            'memberships', 'memberships__trainers')
        if f:  # Don't use ternary !
            # to avoid listing other club memberships
            f['memberships__club'] = self.club
            members = members.filter(**f)

        # Apply club membership
        for m in members:
            m.membership = m.memberships.get(club=self.club)

        # Add last SportWeek date, as week & year
        # Enhance query performance by separating annotation
        # then applying manually the results on queryset
        agg = members.filter(
            sportweek__days__date__lte=date.today()).values('pk').annotate(
            max_date=Max('sportweek__days__date'),
            nb=Count('sportweek__days'))
        agg = dict((a['pk'], (a['max_date'], a['nb'])) for a in agg)
        for m in members:
            m.max_report_date, m.sessions_count = agg.get(m.pk, (None, 0))

        # Sort helpers
        mindate = date(MINYEAR, 1, 1)

        def date_sort(a):
            return a.max_report_date or mindate

        def name_sort(a):
            return a.first_name.lower() + a.last_name.lower()

        # Sort members
        # Using sorted instead of order_by
        # to be able to use added attrs (date)
        default_sort = 'name'
        sort = self.kwargs.get('sort', default_sort)
        sorts = {
            'name': (name_sort, False),
            'name-r': (name_sort, True),
            'date': (date_sort, True),
            'date-r': (date_sort, False),
        }
        if sort not in sorts:
            raise Http404('Invalid sort')
        sort_key, sort_reversed = sorts[sort]
        members = sorted(members, key=sort_key, reverse=sort_reversed)

        return {
            'type': self.kwargs.get('type', default_type),
            'sort': sort,
            'trainers': self.club.members.filter(memberships__role='trainer', memberships__club=self.club).order_by('first_name'),
            'members': members,
        }

    def load_simplified_members(self):
        '''
        Just list the co-members with a club profile available
        for athletes
        For public, list public profile athlets
        '''

        # Sadly, the members list must be constructed as a single filter
        # to avoid users not having club AND valid role
        members = Athlete.objects.filter(
            memberships__club=self.club,
            memberships__role__in=('trainer', 'staff', 'athlete'),
        ).order_by('first_name', 'last_name')
        members = members.prefetch_related('memberships')

        for i, m in enumerate(members):
            m.membership = m.memberships.get(club=self.club)

        return {
            'friends': self.request.user.is_authenticated() and self.request.user.friends.values_list('pk', flat=True) or [],
            'friend_requests': self.request.user.is_authenticated() and self.request.user.requests_sent.values_list('recipient', flat=True) or [],
            'members': members,
        }

    def get_context_data(self, **kwargs):
        context = super(ClubMembers, self).get_context_data(**kwargs)

        if self.role in ('athlete', 'public'):
            # For athletes, list same club athletes
            # For public, list public athletes
            self.template_name = 'club/members.athletes.html'
            context.update(self.load_simplified_members())
        else:
            # For staff/trainers load full lists
            context.update(self.load_members())

        # Add date limits
        today = date.today()
        context['today'] = today
        context['max_diff_date'] = today - timedelta(days=28)
        return context


class ClubMembersExport(ClubMixin, CsvResponseMixin, View):
    '''
    Export the list of members
    as a CSV file
    '''

    def get(self, *args, **kwargs):

        # Headers with trainers
        headers = [
            _('Lastname'),
            _('Firstname'),
            _('Email'),
            _('Role'),
            _('VMA'),
            _('Birthday'),
            _('Trainers'),
        ]

        # Add all data for members
        data = []
        members = self.club.clubmembership_set.filter(
            role__in=('athlete', 'trainer', 'staff'))
        members = members.order_by('user__last_name', 'user__first_name')
        for m in members:
            # Base data
            mdata = {
                _('Lastname'): m.user.last_name,
                _('Firstname'): m.user.first_name,
                _('Email'): m.user.email,
                _('Role'): m.role,
                _('VMA'): m.user.vma,
                _('Birthday'): m.user.birthday,
                _('Trainers'): ' - '.join(m.trainers.values_list('first_name', flat=True)),
            }
            data.append(mdata)

        # Render CSV
        context = {
            'csv_filename': '%s.csv' % self.club.slug,
            'csv_headers': headers,
            'csv_data': data,
        }
        return self.render_to_response(context)
