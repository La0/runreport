# -*- coding: utf-8 -*-
from django.contrib.sites.models import get_current_site
from coffin.shortcuts import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from hashlib import md5
import os

class MailBuilder:
  template = None
  subject = ''
  to = []
  cc = []

  def __init__(self, template):
    self.template = template

  def build(self, context, headers=None):
    # Render template
    site = get_current_site(None)
    message = u'Envoyé via %s' % site
    context.update({
      'site' : site,
    })
    mail_html = render_to_string(self.template, context)
    if settings.DEBUG:
      self.dump(mail_html)

    # Configure mail
    mail = EmailMultiAlternatives(self.subject, message, headers=headers)
    mail.to = self.to
    mail.cc = self.cc

    # Attach the rendered html
    mail.attach_alternative(mail_html, 'text/html')

    # Do not send, it's responsability of caller
    return mail

  def dump(self, html):
    # Dump to static file, for debug only
    h = md5('%s:%s' % (self.template, ':'.join(self.to))).hexdigest()
    path = os.path.join(settings.HOME, 'mails_debug', h + '.html')
    dump = open(path, 'w')
    dump.write(html.encode('utf-8'))
    print 'Dumped mail %s in %s' % (self.subject, path)
