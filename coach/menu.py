# coding=utf-8
from django.core.urlresolvers import reverse

def add_pages(request):
  '''
  List menu pages, with active status
  '''
  def _p(url_name, caption, lazy=False):
    url = reverse(url_name)
    active = lazy and request.path.startswith(url) or (request.path == url)
    return {'url' : url, 'caption' : caption, 'active' : active}

  def _ext(url, caption):
    return {'url' : url, 'caption' : caption, 'active' : False, 'external' : True}

  menu = []
  if request.user.is_authenticated():
    menu.append(_p('report-current', 'Cette semaine'))
    menu.append(_p('report-current-month', 'Calendrier', True))

    # Club menu
    submenu = {
      'caption' : 'Le club',
      'menu' : []
    }
    submenu['menu'].append(_ext('http://csternes.athle.org', 'Site officiel'))
    submenu['menu'].append(_ext('http://facebook.com/groups/USA17', 'Groupe Facebook'))
    menu.append(submenu)

    # User menu
    submenu = {
      'caption' : request.user.first_name or request.user.username,
      'menu' : []
    }
    submenu['menu'].append(_p('user-profile', 'Mon profil'))
    submenu['menu'].append(_p('logout', u'Se déconnecter'))
    menu.append(submenu)
  else:
    menu.append(_p('user-create', u'Créer un compte'))
    menu.append(_p('login', 'Se connecter'))

  return {
    'menu' : menu,
  }
