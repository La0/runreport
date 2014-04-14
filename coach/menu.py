# coding=utf-8
from django.core.urlresolvers import reverse
from club.models import ClubMembership

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

  def _build_help():
    # Build help menu with contact & news
    submenu = {
      'caption' : 'Aide',
      'menu' : [],
      'icon' : 'icon-help-circled',
    }
    submenu['menu'].append(_p(('page-list', 'help'), 'Aide', lazy=True))
    submenu['menu'].append(_p(('page-list', 'news'), 'News', lazy=True))
    submenu['menu'].append(_p(('contact_form',), 'Contact', lazy=True))
    return submenu

  menu = []
  if request.user.is_authenticated():
    menu.append(_p('report-current', 'Semaine', 'icon-list'))
    menu.append(_p('report-current-month', 'Calendrier', icon='icon-calendar', lazy=True))

    # Build Club menu
    members = ClubMembership.objects.filter(user=request.user).exclude(role__in=('archive', 'prospect'))
    for m in members:
      submenu = {
        'caption' : m.club.name,
        'menu' : [],
        'icon' : 'icon-star',
      }

      # Add club admin links for trainers
      if m.role in ('trainer', 'staff') or request.user.is_superuser:
        submenu['menu'].append(_p(('club-current-name', m.club.slug, 'athletes', 'name'), u'Mes Athlètes'))
        submenu['menu'].append(_p(('club-races', m.club.slug, ), u'Les courses', lazy=True))
        submenu['menu'].append(_p(('plans', ), u'Mes plans', lazy=True))

        # Manage links
        if m.club.manager == request.user or request.user.is_superuser:
          submenu['menu'].append(_p(('club-current-name', m.club.slug, 'prospects', 'name'), u'Nouveaux'))
          submenu['menu'].append(_p(('club-current-name', m.club.slug, 'all', 'name'), u'Tout le club'))
          submenu['menu'].append(_p(('club-current-name', m.club.slug, 'archives', 'name'), u'Archives'))
          submenu['menu'].append(_p(('club-manage', m.club.slug), u'Administrer'))

        submenu['menu'].append('__SEPARATOR__')

      # Add public club links for everyone
      for link in m.club.links.all().order_by('position'):
        submenu['menu'].append(_ext(link.url, link.name))

      menu.append(submenu)

    # Add button to join a club
    # when no memberships exist
    if not members:
      menu.append(_p('club-list', 'Rejoindre un club', 'icon-plus'))

    # Help menu
    menu.append(_build_help())

    # User menu
    submenu = {
      'caption' : request.user.first_name or request.user.username,
      'menu' : [],
      'icon' : 'icon-user',
    }
    submenu['menu'].append(_p('user-profile', 'Mon profil'))
    submenu['menu'].append(_p('vma', 'Mes allures'))
    submenu['menu'].append(_p('user-races', 'Mes records'))
    submenu['menu'].append(_p('user-garmin', u'Données Garmin'))
    submenu['menu'].append(_p('vma-glossary', 'Glossaire'))
    submenu['menu'].append('__SEPARATOR__')
    submenu['menu'].append(_p('logout', u'Se déconnecter'))
    menu.append(submenu)
  else:
    menu.append(_p('user-create', u'Créer un compte', 'icon-plus'))
    menu.append(_build_help())
    menu.append(_p('login', 'Se connecter', 'icon-user'))

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
