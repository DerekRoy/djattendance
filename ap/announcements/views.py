import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from braces.views import GroupRequiredMixin

from ap.forms import TraineeSelectForm
from aputils.trainee_utils import is_TA, trainee_from_user
from aputils.decorators import group_required
from aputils.utils import modify_model_status

from .models import Announcement
from .forms import AnnouncementForm, AnnouncementTACommentForm, AnnouncementDayForm

class AnnouncementRequest(generic.edit.CreateView):
  model = Announcement
  template_name = 'announcement_form.html'
  form_class = AnnouncementForm

  def get_form_kwargs(self):
    kwargs = super(AnnouncementRequest, self).get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def get_context_data(self, **kwargs):
    context = super(AnnouncementRequest, self).get_context_data(**kwargs)
    context['trainee_select_form'] = TraineeSelectForm()
    return context

  def form_valid(self, form):
    req = form.save(commit=False)
    req.trainee_author = trainee_from_user(self.request.user)
    req.save()
    form.save_m2m()
    return super(AnnouncementRequest, self).form_valid(form)

class AnnouncementRequestList(generic.ListView):
  model = Announcement
  template_name = 'requests/request_list.html'

  def get_queryset(self):
    if is_TA(self.request.user):
      return Announcement.objects.filter().order_by('status')
    else:
      trainee = trainee_from_user(self.request.user)
      return Announcement.objects.filter(trainee_author=trainee).order_by('status')

class AnnouncementDetail(generic.DetailView):
  model = Announcement
  template_name = 'requests/detail_request.html'
  context_object_name = 'announcement'

class AnnouncementDelete(generic.DeleteView):
  model = Announcement
  success_url = reverse_lazy('announcements:announcement-request-list')

class AnnouncementUpdate(generic.UpdateView):
  model = Announcement
  template_name = 'announcement_form.html'
  form_class = AnnouncementForm

  def get_form_kwargs(self):
    kwargs = super(AnnouncementUpdate, self).get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def get_context_data(self, **kwargs):
    context = super(AnnouncementUpdate, self).get_context_data(**kwargs)
    context['trainee_select_form'] = TraineeSelectForm()
    return context

class AnnouncementList(GroupRequiredMixin, generic.ListView):
  model = Announcement
  template_name = 'announcements_day.html'
  group_required = ['administration']

  def dispatch(self, request, *args, **kwargs):
    date_string = self.kwargs.get('date', None)
    if not date_string:
      date = datetime.date.today()
    else:
      date = datetime.datetime.strptime(date_string, "%m-%d-%Y").date()
    self.date = date
    return super(AnnouncementList, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(AnnouncementList, self).get_context_data(**kwargs)
    context['date'] = self.date
    context['form'] = AnnouncementDayForm()
    return context

  def get_queryset(self):
    announcements = Announcement.objects \
    .filter(type='CLASS',
      status='A',
      announcement_date=self.date
    )
    return announcements

class TAComment(GroupRequiredMixin, generic.UpdateView):
  model = Announcement
  template_name = 'requests/ta_comments.html'
  form_class = AnnouncementTACommentForm
  group_required = ['administration']
  raise_exception = True
  success_url = reverse_lazy('announcements:announcement-request-list')

  def get_context_data(self, **kwargs):
    context = super(TAComment, self).get_context_data(**kwargs)
    context['item_name'] = Announcement._meta.verbose_name
    return context

class AnnouncementsRead(generic.ListView):
  model = Announcement
  template_name = 'announcements_read.html'

  def get_queryset(self):
    trainee = trainee_from_user(self.request.user)
    announcements = Announcement.objects.filter(trainees_read=trainee)
    return announcements

modify_status = modify_model_status(Announcement, reverse_lazy('announcements:announcement-request-list'))

def mark_read(request, id):
  announcement = get_object_or_404(Announcement, pk=id)
  trainee = trainee_from_user(request.user)
  announcement.trainees_show.remove(trainee)
  announcement.trainees_read.add(trainee)
  announcement.save()
  return redirect('home')
