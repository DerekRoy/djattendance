from django import forms

from accounts.widgets import TraineeSelect2MultipleInput
from graduation.models import Testimony, Consideration, Website, Outline, Misc, GradAdmin
from aputils.widgets import DatePicker


class GenericModelForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(GenericModelForm, self).__init__(*args, **kwargs)

  class Meta:
    exclude = ['trainee', 'due_date', 'show_status', 'grad_admin', ]


class TestimonyForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Testimony


class ConsiderationForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Consideration


class WebsiteForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Website


class OutlineForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Outline


class MiscForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Misc


class GradAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(GradAdminForm, self).__init__(*args, **kwargs)

  class Meta:
    model = GradAdmin
    exclude = ['term', ]
    widgets = {
      'testimony_due_date': DatePicker(),
      'consideration_due_date': DatePicker(),
      'website_due_date': DatePicker(),
      'outline_due_date': DatePicker(),
      'misc_due_date': DatePicker(),
      'speaking_trainees': TraineeSelect2MultipleInput(attrs={'id': 'id_trainees'}),
    }
