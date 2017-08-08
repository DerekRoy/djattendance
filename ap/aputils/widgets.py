from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.templatetags.admin_static import static
from django.forms.widgets import DateInput, TimeInput, RadioSelect, SelectMultiple
from django_select2.forms import Select2MultipleWidget

from services.serializers import ServiceCalendarSerializer
from rest_framework.renderers import JSONRenderer


class DatePicker(DateInput):
  format = '%m/%d/%Y'

  def __init__(self, *args, **kwargs):
    kwargs['attrs'] = {'class': 'datepicker'}
    super(DatePicker, self).__init__(*args, **kwargs)

  class Media:
    js = (
      'js/datepicker.js',
    )


class MultipleSelectFullCalendar(SelectMultiple):
  def __init__(self, queryset, name, attrs=None, choices=()):
    self.queryset = queryset
    self.name = name
    super(MultipleSelectFullCalendar, self).__init__(attrs, choices)

  def render(self, name, value, attrs=None, choices=()):
    # print name, value, choices, self.choices
    services = JSONRenderer().render(ServiceCalendarSerializer(self.queryset, many=True).data)
    selected = ",".join(str(x) for x in value) if value is not None else ""
    context = {'services': services, 'selected': selected}
    return render_to_string('MultipleSelectFullCalendar.html', context) + super(MultipleSelectFullCalendar, self).render(name, value, attrs, choices)

  class Media:
    css = {
      'all': (
         'css/fullcalendar.css',
      )
    }
    js = (
      'js/moment.min.js',
      'js/fullcalendar.js',
      'js/jquery.xcolor.js',
      'js/fullcalendar_init.js',
    )

class PlusSelect2MultipleWidget(Select2MultipleWidget):
  def render(self, name, value, attrs=None, choices=()):
    output = super(PlusSelect2MultipleWidget, self).render(name, value, attrs, choices)
    link = []
    rel_to = self.choices.queryset.model
    info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
    related_url = reverse('admin:%s_%s_add' % info, current_app='admin') + '?_to_field=id&amp;_popup=1'
    link.append(u'<a href="%s" class="related-widget-wrapper-link add-related" id="add_id_%s"> ' % (related_url, name))
    link.append(u'<img src="%s" width="10" height="10" alt="%s"/></a>'
                % (static('admin/img/icon_addlink.gif'), _('Add Another')))
    return output + mark_safe(u''.join(link))
