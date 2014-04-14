# -*- encoding: utf-8 -*-
# Gist : https://gist.github.com/michelts/1029336
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import csv


class MultipleFormsMixin(ModelFormMixin):
    """
    A mixin that provides a way to show and handle several forms in a
    request.
    """
    form_classes = {} # set the form classes as a mapping
    instances = {} # Object instances may be used to init forms
    object = None

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes):
        return dict([(key, klass(**self.get_form_kwargs(key))) \
            for key, klass in form_classes.items()])

    def get_form_kwargs(self, key):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ModelFormMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.get_instance(key)})
        return kwargs

    def get_instance(self, key):
      return self.instances.get(key, None)

    def forms_valid(self, forms):
        return super(MultipleFormsMixin, self).form_valid(forms)

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))


class ProcessMultipleFormsView(ProcessFormView):
    """
    A mixin that processes multiple forms on POST. Every form must be
    valid.
    """
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultipleFormsMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """

class MultipleFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaing several forms, and rendering a template response.
    """

JSON_STATUS_OK = 'ok'
JSON_STATUS_LOAD = 'load' # Load an url
JSON_STATUS_ERROR = 'error'

JSON_OPTION_BODY_RELOAD = 'body_reload' # Reload the body (source)
JSON_OPTION_NO_HTML = 'nohtml' # No output
JSON_OPTION_CLOSE = 'close' # Close modal
JSON_OPTION_REDIRECT_SKIP = 'redirect_skip' # Skip http redirect

class JsonResponseMixin(object):
  """
  A mixin that renders response to some json
  """
  json_status = JSON_STATUS_OK # Response inner status
  json_options = []

  def render_to_response(self, context):
    # Render normally html, using parents code
    html = None
    if JSON_OPTION_NO_HTML not in self.json_options:
      parent = super(JsonResponseMixin, self).render_to_response(context)
      html = parent.rendered_content
    return self.build_response(html=html)

  def build_response(self, html=None, message=None, url=None):
    # Base output
    data = {
      'status' : self.json_status,
      'options' : self.json_options,
    }

    # Add optional datas
    if url is not None:
      data['url'] = url
    if html is not None:
      data['html'] = html
    if message is not None:
      data['message'] = message
    return HttpResponse(json.dumps(data), content_type='application/json')

  def dispatch(self, *args, **kwargs):
    # Catch all reponses
    try:
      resp = super(JsonResponseMixin, self).dispatch(*args, **kwargs)
    except Exception, e:
      print "Json Dispatch failed: %s" % str(e)
      if settings.DEBUG:
        # Raise with call stack
        import sys
        exc = sys.exc_info()
        raise exc[0], exc[1], exc[2]

      # Base error response
      self.json_status = JSON_STATUS_ERROR
      return self.build_response(message=str(e))

    # Catch redirection
    if isinstance(resp, HttpResponseRedirect) and JSON_OPTION_REDIRECT_SKIP not in self.json_options:
      self.json_status = JSON_STATUS_LOAD
      self.json_options = []
      return self.build_response(url=resp['Location'])

    return resp

class CsvResponseMixin(object):
  '''
  This mixin render a response using csv writer
   and add HTTP header to donwload this render.
  '''
  def render_to_response(self, context):
    if 'csv_data' not in context:
      return super(CsvResponseMixin, self).render_to_response(context)

    # Prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % context.get('csv_filename', 'output')

    response.write(u'\ufeff'.encode('utf8'))

    # Add data in response
    writer = csv.writer(response, delimiter=';', dialect='excel')
    for line in context['csv_data']:
      writer.writerow(line)

    return response

