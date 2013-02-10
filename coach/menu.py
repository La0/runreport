# coding=utf-8
from django.core.urlresolvers import reverse

def add_pages(request):
  '''
  List menu pages, with active status
  '''
  def _p(url_name, caption):
    url = reverse(url_name) 
    return {'url' : url, 'caption' : caption, 'active' : (request.path == url)}

  menu = []
  if request.user.is_authenticated():
    menu.append(_p('report-current', 'Cette semaine'))
    menu.append(_p('user-profile', 'Mon profil'))
    menu.append(_p('logout', u'Se déconnecter'))
  else:
    menu.append(_p('user-create', u'Créer un compte'))
    menu.append(_p('login', 'Se connecter'))

  return {
    'menu' : menu,
  }
