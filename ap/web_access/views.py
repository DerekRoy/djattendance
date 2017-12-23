from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.http import HttpResponse

from braces.views import GroupRequiredMixin


from .forms import WebAccessRequestCreateForm, WebAccessRequestTACommentForm, WebAccessRequestGuestCreateForm, DirectWebAccess, EShepherdingRequest
from .models import WebRequest
from . import utils
from aputils.trainee_utils import trainee_from_user, is_TA
from aputils.decorators import group_required
from aputils.utils import modify_model_status


class WebAccessCreate(generic.CreateView):
  model = WebRequest
  template_name = 'requests/request_form.html'
  form_class = WebAccessRequestCreateForm

  def form_valid(self, form):
    req = form.save(commit=False)
    req.trainee = trainee_from_user(self.request.user)
    req.save()
    message = "Created new web request."
    messages.add_message(self.request, messages.SUCCESS, message)
    return super(WebAccessCreate, self).form_valid(form)


class WebAccessUpdate(generic.UpdateView):
  model = WebRequest
  template_name = 'requests/request_form.html'
  form_class = WebAccessRequestCreateForm


class WebAccessDelete(generic.DeleteView):
  model = WebRequest


class WebAccessDetail(generic.DetailView):
  model = WebRequest
  template_name = 'requests/detail_request.html'


class WebRequestList(generic.ListView):
  model = WebRequest
  template_name = 'web_access/web_access_list.html'

  def get_queryset(self):
    trainee = trainee_from_user(self.request.user)
    if is_TA(self.request.user):
      return WebRequest.objects.filter().order_by('status')
    else:
      return WebRequest.objects.filter(trainee=trainee).order_by('status')


class TAWebAccessUpdate(GroupRequiredMixin, generic.UpdateView):
  model = WebRequest
  template_name = 'requests/ta_comments.html'
  form_class = WebAccessRequestTACommentForm
  group_required = ['administration']
  raise_exception = True


modify_status = modify_model_status(WebRequest, reverse_lazy('web_access:web_access-list'))


def getGuestRequests(request):
  """ Returns list of requests identified by MAC address """
  mac = utils._getMAC(utils._getIPAddress(request))
  requests = WebRequest.objects.all().filter(trainee=None, mac_address=mac).order_by('status')
  print mac
  html = render(request, 'web_access/requests_panel.html', context={'guest_access_requests': requests})
  return HttpResponse(html)


def eShepherdingRequest(request):
  if request.method == 'POST':
    form = EShepherdingRequest(request.POST)
    if form.is_valid():
      mac = utils._getMAC(utils._getIPAddress(request))
      if mac is not None:
        utils.startAccessFromMacAddress(request, '30', mac)
      else:
        message = "Mac address location failed."
        messages.add_message(request, messages.ERROR, message)
      return redirect('web_access:eshepherding-access')
  else:
    form = EShepherdingRequest()
  return render(request, 'web_access/eshepherding_access.html', {'form': form})


def createGuestWebAccess(request):
  if request.method == 'POST':
    mac = utils._getMAC(utils._getIPAddress(request))
    form = WebAccessRequestGuestCreateForm(request.POST)
    if form.is_valid():
      instance = form.save(commit=False)
      instance.mac_address = mac
      instance.save()
    return HttpResponse('Submitted!')
  else:
    return HttpResponse('Error: This is a private endpoint, only accept post')


def deleteGuestWebAccess(request, id):
  WebRequest.objects.filter(id=id).delete()
  return getGuestRequests(request)


@group_required(('administration', 'networks'), raise_exception=True)
def directWebAccess(request):
  if request.method == 'POST':
    form = DirectWebAccess(request.POST)
    if form.is_valid():
      utils.startAccessFromMacAddress(
          request,
          form.cleaned_data.get('minutes'),
          form.cleaned_data.get('mac_address')
      )
      return redirect('web_access:direct-web-access')
  else:
    form = DirectWebAccess()

  return render(request, 'web_access/direct_web_access.html', {'form': form})
