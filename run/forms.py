from models import RunSession
from django.forms.models import modelformset_factory

# Init Form set factory
RunSessionFormSet = modelformset_factory(RunSession, fields=('comment', ), extra=0)
