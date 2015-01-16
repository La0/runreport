from django.template.loader import BaseLoader
from django.template import TemplateDoesNotExist
from django.conf import settings
import jinja2
from coffin.template.loader import get_template

from django.template.loaders import app_directories
from django.template.loaders import filesystem


class LoaderMixin(object):
  is_usable = True

  def load_template(self, template_name, template_dirs=None):

    # Render packages apps with django system
    pos = template_name.find('/')
    folder = pos and template_name[0:pos] or None
    if folder in ('admin', 'debug_toolbar', 'rest_framework', ):
      return super(LoaderMixin, self).load_template(template_name, template_dirs)

    # Render through Jinja
    try:
      template = get_template(template_name)
    except jinja2.TemplateNotFound, e:
      if settings.DEBUG:
        print "Jinja loader failed: %s" % str(e)
      raise TemplateDoesNotExist(template_name)
    return template, template.filename


class FileSystemLoader(LoaderMixin, filesystem.Loader):
  pass

class AppLoader(LoaderMixin, app_directories.Loader):
  pass
