from django.template.loader import BaseLoader
from django.template import TemplateDoesNotExist
from django.conf import settings
import jinja2
from coffin.template.loader import get_template

class Loader(BaseLoader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        if template_name.startswith('admin/'):
          raise TemplateDoesNotExist(template_name)
        try:
            template = get_template(template_name)
        except jinja2.TemplateNotFound, e:
            if settings.DEBUG:
              print "Jinja loader failed: %s" % str(e)
            raise TemplateDoesNotExist(template_name)
        return template, template.filename
