# coding=utf-8
from django.core.urlresolvers import reverse
from club.models import ClubMembership

def add_pages(request):
  '''
  List menu pages, with active status
  '''
  def _p(url_tuple, caption, lazy=False):
    url_name = isinstance(url_tuple, tuple) and url_tuple[0] or url_tuple
    url_args = isinstance(url_tuple, tuple) and url_tuple[1:] or ()
    url = reverse(url_name, args=url_args)
    active = lazy and request.path.startswith(url) or (request.path == url)
    return {'url' : url, 'caption' : caption, 'active' : active}

  def _ext(url, caption):
    return {'url' : url, 'caption' : caption, 'active' : False, 'external' : True}

  menu = []
  if request.user.is_authenticated():
    menu.append(_p('report-current', 'Cette semaine'))
    menu.append(_p('report-current-month', 'Calendrier', True))

    # Build Club menu
    members = ClubMembership.objects.filter(user=request.user)
    for m in members:
      submenu = {
        'caption' : m.club.name,
        'menu' : []
      }

      # Add club admin links for trainers
      if m.role == 'trainer' or request.user.is_superuser:
        submenu['menu'].append(_p(('club-current-name', m.club.slug, 'athletes', 'name'), u'Mes Athlètes'))
        submenu['menu'].append(_p(('club-current-name', m.club.slug, 'all', 'name'), u'Tout le club'))
        submenu['menu'].append(_p(('club-current-name', m.club.slug, 'archives', 'name'), u'Archives'))
        submenu['menu'].append('__SEPARATOR__')

      # Add public club links for everyone
      for link in m.club.links.all().order_by('position'):
        submenu['menu'].append(_ext(link.url, link.name))

      menu.append(submenu)

    # User menu
    submenu = {
      'caption' : request.user.first_name or request.user.username,
      'menu' : []
    }
    submenu['menu'].append(_p('vma', 'Mes allures'))
    submenu['menu'].append(_p('user-profile', 'Mon profil'))
    submenu['menu'].append(_p('vma-glossary', 'Glossaire'))
    submenu['menu'].append(_p('logout', u'Se déconnecter'))
    menu.append(submenu)
  else:
    menu.append(_p('user-create', u'Créer un compte'))
    menu.append(_p('login', 'Se connecter'))

  return {
    'menu' : menu,
  }
