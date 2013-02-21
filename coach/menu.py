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

  menu = []
  if request.user.is_authenticated():
    menu.append(_p('report-current', 'Cette semaine'))
    menu.append(_p('report-current-month', 'Calendrier', True))
    menu.append(_p('user-profile', 'Mon profil'))
    menu.append(_p('logout', u'Se déconnecter'))
  else:
    menu.append(_p('user-create', u'Créer un compte'))
    menu.append(_p('login', 'Se connecter'))

  return {
    'menu' : menu,
  }
