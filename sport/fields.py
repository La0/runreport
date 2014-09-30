from datetime import timedelta
from django.forms import TextInput, Field
from helpers import seconds_humanize
import re
TIME_FORMATS = [
  '(?P<hour>\d+):(?P<min>\d+):(?P<sec>\d+)',
  '(?P<hour>\d+)(:|h|H)(\s?)(?P<min>\d+)',
  '(?P<min>\d+)min',
]

# Convert from any format to seconds
TIME_MULTIPLES = {
  'day' : 24 * 3600,
  'hour' : 3600,
  'min' : 60,
  'sec' : 1,
}

class IntervalWidget(TextInput):
  def _format_value(self, value):

    # Format timedelta as HH:MM:SS
    if isinstance(value, timedelta):
      return seconds_humanize(value.total_seconds())

    return value

class IntervalFormField(Field):

  def __init__(self, *args, **kwargs):
    super(IntervalFormField, self).__init__(*args, **kwargs)

  def clean(self, value):
    # By default, not required
    if not value:
      return None

    # Search valid time format
    for time_format in TIME_FORMATS:
      matches = re.match(time_format, value)
      if matches:
        seconds = 0.0
        parsed = matches.groupdict()

        # Build timedelta from seconds
        seconds = sum([float(value) * TIME_MULTIPLES[name] for name, value in matches.groupdict().items()])
        return timedelta(seconds=seconds)

    raise forms.ValidationError('Format de temps non reconnu.')

