# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from django.db.models import Sum

from terms.models import Term
from graduation.models import *
from graduation.forms import *

from braces.views import GroupRequiredMixin

from datetime import datetime
from itertools import chain
from operator import attrgetter


class CreateUpdateView(UpdateView):
  template_name = 'graduation/graduation_form.html'

  def get_object(self, queryset=None):
    grad_admin, created = GradAdmin.objects.get_or_create(term=Term.current_term())
    obj, created = self.model.objects.get_or_create(trainee=self.request.user, grad_admin=grad_admin)
    return obj

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(CreateUpdateView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(CreateUpdateView, self).post(request, *args, **kwargs)

  def form_valid(self, form):
    return super(CreateUpdateView, self).form_valid(form)

  def get_context_data(self, **kwargs):
    ctx = super(CreateUpdateView, self).get_context_data(**kwargs)
    today = datetime.now().date()
    if self.object.show_status == 'SHOW' or today > self.object.due_date:
      ctx['read_only'] = True
    ctx['page_title'] = self.object.name
    ctx['button_label'] = 'Save'
    return ctx


class TestimonyView(CreateUpdateView):
  model = Testimony
  form_class = TestimonyForm

  template_name = 'graduation/testimony.html'


class ConsiderationView(CreateUpdateView):
  model = Consideration
  form_class = ConsiderationForm

  template_name = 'graduation/consideration.html'


class WebsiteView(CreateUpdateView):
  model = Website
  form_class = WebsiteForm


class OutlineView(CreateUpdateView):
  model = Outline
  form_class = OutlineForm

  template_name = 'graduation/outline.html'

class RemembranceView(CreateUpdateView):
  model = Remembrance
  form_class = RemembranceForm

class MiscView(CreateUpdateView):
  model = Misc
  form_class = MiscForm


class GradAdminView(UpdateView, GroupRequiredMixin):
  model = GradAdmin
  form_class = GradAdminForm
  template_name = 'graduation/grad_admin.html'
  group_required = ['training_assistant', 'grad_committee']

  def get_object(self, queryset=None):
    obj, created = self.model.objects.get_or_create(term=Term.current_term())
    return obj

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(GradAdminView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(GradAdminView, self).post(request, *args, **kwargs)

  def form_valid(self, form):
    return super(GradAdminView, self).form_valid(form)

  def get_statistics(self):
    term = Term.current_term()
    return {
        'Testimony responses': Testimony.responded_number(term),
        'Consideration responses': Consideration.responded_number(term),
        'Website responses': Website.responded_number(term),
        'Outline responses': Outline.responded_number(term),
        'Remembrance responses': Remembrance.responded_number(term),
        'Misc responses': Misc.responded_number(term),
    }

  def get_context_data(self, **kwargs):
    ctx = super(GradAdminView, self).get_context_data(**kwargs)
    ctx['stats'] = self.get_statistics()
    ctx['page_title'] = "Grad Admin"
    ctx['button_label'] = 'Save'
    return ctx

class MiscReport(ListView):
  model = Misc
  template_name = 'graduation/misc_report.html'

  def get_context_data(self, **kwargs):
    context = super(MiscReport, self).get_context_data(**kwargs)
    
    ct = Term.objects.filter(current=True).first()
    ga = GradAdmin.objects.get(term=ct)
    misc = Misc.objects.filter(grad_admin=ga, trainee__in=Trainee.objects.filter(current_term=4))
    rem = Remembrance.objects.filter(grad_admin=ga, trainee__in=Trainee.objects.filter(current_term=4))
    m = [i for i in misc if i.responded]
    r = [i for i in rem if i.responded]

    result_list = sorted(chain(m, r), key=attrgetter('trainee'))
    
    context = {
      'invite_count': misc.aggregate(Sum('grad_invitations')),
      'dvd_count': misc.aggregate(Sum('grad_dvd')),
      'list': result_list,

    }
    return context

class TestimonyReport(ListView):
  model = Testimony
  template_name = 'graduation/testimony_report.html'

class ConsiderationReport(ListView):
  model = Consideration
  template_name = 'graduation/consideration_report.html'

  def get_context_data(self, **kwargs):
    context = super(ConsiderationReport, self).get_context_data(**kwargs)

    cons = Consideration.objects.all()
    c = [i for i in cons if i.responded]

    context = {
      'data': c
    }
    return context

class WebsiteReport(ListView):
  model = Website
  template_name = 'graduation/consideration_report.html'

class OutlineReport(ListView):
  model = Outline
  template_name = 'graduation/outline_report.html'