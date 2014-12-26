from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.db.models import Min, Max
from django.utils import timezone
from post.models import Post

class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    fields = ('title', 'slug', 'html', 'published', 'type', )

class YearMonthForm(forms.Form):
  date = forms.DateField(widget=SelectDateWidget())

  def __init__(self, user, *args, **kwargs):
    super(YearMonthForm, self).__init__(*args, **kwargs)

    # Get min & max year for user's SportWeek
    agg = user.sportweek.aggregate(min=Min('year'), max=Max('year'))
    now = timezone.now()
    min = agg.get('min', None) or now.year
    max = agg.get('max', None) or now.year
    years = range(min, max+1)
    years.reverse()
    self.fields['date'].widget.years = years
