from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.contrib import messages
from meal_seating.models import Table, TraineeExclusion
from accounts.models import Trainee
from datetime import date, timedelta
from django.views.generic import TemplateView, DetailView, ListView
from django.views import generic
from terms.models import Term
from accounts.models import Trainee
from .serializers import TableSerializer

from rest_framework import viewsets, filters
from rest_framework.renderers import JSONRenderer
from rest_framework_bulk import BulkModelViewSet


@csrf_protect
def editinfo(request):
  test = request.POST.getlist('to')
  print test
  isChecked = [int(x) for x in request.POST.getlist('to[]')]
  print set(isChecked)
  exclude_list = get_exclude_list()
  difference = set(exclude_list) - set(isChecked)
  addition = set(isChecked) - set(exclude_list)
  TraineeExclusion.objects.all().filter(trainee__in=list(difference)).delete()
  trainee_exclusions = [TraineeExclusion(trainee=val) for val in addition]
  TraineeExclusion.objects.bulk_create(trainee_exclusions)
  return HttpResponse(difference)

def get_exclude_list():
  exclude_list = TraineeExclusion.objects.values_list('trainee', flat=True)
  return exclude_list if exclude_list else []

def seattables(request):
  filterchoice = request.POST['Filter']
  genderchoice = request.POST['Gender']
  startdate = request.POST['startdate']
  enddate = request.POST['enddate']

  trainees = Trainee.objects.all().filter(gender=genderchoice).order_by(filterchoice).exclude(id__in=get_exclude_list())
  seating_list = Table.seatinglist(trainees,genderchoice)
  if seating_list == None:
    messages.error(request, 'Not enough seats available!')
    return redirect('/meal_seating')
  else:
    return render(request, 'meal_seating/detail.html', {'seating_list' : seating_list, 'startdate':startdate, 'enddate': enddate})

def newseats(request):
  exclude_list = get_exclude_list()
  trainees_exclude = Trainee.objects.filter(pk__in=exclude_list)
  trainees = Trainee.objects.filter(is_active=1).exclude(type="S").order_by("lastname")
  return render(request, 'meal_seating/index.html', {'trainees' : trainees,'exclude_list':trainees_exclude,})

def signin(request):
  trainees = Trainee.objects.all().filter(is_active=1).order_by("lastname")
  startdate = date.today()
  two_week_datelist = []
  for x in range(0,14):
    mydate = startdate + timedelta(days=x)
    two_week_datelist.append(format(mydate))
  return render(request, 'meal_seating/mealsignin.html', {'trainees' : trainees, 'start_date' : startdate, "two_week_datelist" : two_week_datelist})

class TableListView(generic.ListView):
  model = Table
  template_name = 'meal_seating/table_edit.html'

  context_object_name = 'context'

  def get_context_data(self, **kwargs):
    listJSONRenderer = JSONRenderer()
    l_render = listJSONRenderer.render
    table = Table.objects.all().order_by('name')
    context = super(TableListView, self).get_context_data(**kwargs)
    context['table_bb'] = l_render(TableSerializer(table, many=True).data)
    return context

class TableViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows tables to be viewed or edited.
  """
  queryset = Table.objects.all()
  serializer_class = TableSerializer
