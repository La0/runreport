# coding=utf-8
from django.core.urlresolvers import reverse
from club.models import ClubMembership
from users.notification import UserNotifications
from django.utils.translation import ugettext_lazy as _

def add_pages(request):
  '''
  List menu pages, with active status
  '''
  def _p(url_tuple, caption, icon=False, lazy=False):
    url_name = isinstance(url_tuple, tuple) and url_tuple[0] or url_tuple
    url_args = isinstance(url_tuple, tuple) and url_tuple[1:] or ()
    url = reverse(url_name, args=url_args)
    active = lazy and request.path.startswith(url) or (request.path == url)
    return {'url' : url, 'caption' : caption, 'active' : active, 'icon': icon}

  def _ext(url, caption):
    return {'url' : url, 'caption' : caption, 'active' : False, 'external' : True}

  def _build_club_generic():
    return {
      'caption' : _('Clubs'),
      'menu': [
        _p('club-list', _('View clubs')),
        _p('club-landing', _('Create a club')),
      ],
      'icon' : 'icon-star',
    }

  def _build_help():
    # Build help menu with contact & news
    submenu = {
      'caption' : _('Help'),
      'menu' : [],
      'icon' : 'icon-help-circled',
    }
    submenu['menu'].append(_p(('page-list', 'help'), _('Help'), lazy=True))
    submenu['menu'].append(_p('vma-glossary', _('Glossary')))
    submenu['menu'].append(_p(('page-list', 'news'), _('News'), lazy=True))
    submenu['menu'].append(_p(('contact_form',), _('Contact'), lazy=True))
    return submenu

  menu = []
  if request.user.is_authenticated():
    menu.append(_p('report-current', _('This Week'), 'icon-list'))
    menu.append(_p('report-current-month', _('Calendar'), icon='icon-calendar', lazy=True))

    # Load memberships
    members = request.user.memberships.exclude(role__in=('archive', 'prospect'))

    # Build generic club menu
    menu.append(_build_club_generic())

    # Build Club menu
    for m in members:
      submenu = {
        'caption' : m.club.name,
        'menu' : [],
        'icon' : 'icon-club',
      }

      # Add club list for athletes
      if m.role in ('athlete', ):
        submenu['menu'].append(_p(('club-members', m.club.slug), _('Members')))
        submenu['menu'].append('__SEPARATOR__')

      # Add club admin links for trainers
      if m.role in ('trainer', 'staff') or request.user.is_superuser:
        submenu['menu'].append(_p(('club-members-name', m.club.slug, 'athletes', 'name'), _('My athletes')))
        submenu['menu'].append(_p(('club-races', m.club.slug, ), _('Races'), lazy=True))
        # Removed plans because non functional
        #submenu['menu'].append(_p(('plans', ), u'Mes plans', lazy=True))
        submenu['menu'].append(_p(('club-members-name', m.club.slug, 'all', 'name'), _('All the club')))

        # Manage links
        if m.club.manager == request.user or request.user.is_superuser:
          submenu['menu'].append(_p(('club-members-name', m.club.slug, 'prospects', 'name'), _('Newcomers')))
          submenu['menu'].append(_p(('club-members-name', m.club.slug, 'archives', 'name'), _('Archives')))
          submenu['menu'].append(_p(('club-manage', m.club.slug), _('Manage')))

        submenu['menu'].append('__SEPARATOR__')

      # Add public club links for everyone
      for link in m.club.links.all().order_by('position'):
        submenu['menu'].append(_ext(link.url, link.name))

      menu.append(submenu)

    # Help menu
    menu.append(_build_help())

    # Show notifications count
    un = UserNotifications(request.user)
    nb_notif = un.total()
    menu.append({
      'notifications' : nb_notif,
    })

    # User menu
    submenu = {
      'caption' : request.user.first_name or request.user.username,
      'menu' : [],
      'icon' : 'icon-user',
    }
    submenu['menu'].append(_p('message-inbox', _('My messages')))
    submenu['menu'].append(_p('user-preferences', _('My preferences')))
    submenu['menu'].append(_p(('user-public-profile', request.user.username), _('My public profile')))
    submenu['menu'].append(_p('stats', _('My statistics'), lazy=True))
    submenu['menu'].append(_p('vma', _('My paces')))
    submenu['menu'].append(_p('user-races', _('My records')))
    submenu['menu'].append(_p('user-garmin', _('Garmin Sync')))
    submenu['menu'].append('__SEPARATOR__')
    submenu['menu'].append(_p('logout', _('Logout')))
    menu.append(submenu)
  else:
    menu.append(_p('user-create', _('Create an account'), 'icon-plus'))
    menu.append(_build_club_generic())
    menu.append(_build_help())
    menu.append(_p('login', _('Login'), 'icon-user'))

  # Search for active main menu
  # based on sub items
  for m in menu:
    if 'menu' not in m: continue
    if len([l['active'] for l in m['menu'] if isinstance(l, dict) and l['active']]):
      m['active'] = True
      break

  return {
    'menu' : menu,
  }
