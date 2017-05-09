from django.conf.urls import url
from django.conf import settings

from schedules import views

urlpatterns = [
    url(r'schedule/$', views.SchedulePersonal.as_view(), name='schedule'),
    url(r'event/create/$', views.EventCreate.as_view(), name='event-create'),
    url(r'event/(?P<pk>\d+)/$', views.EventDetail.as_view(), name='event-detail'),
    url(r'event/(?P<pk>\d+)/update/$', views.EventUpdate.as_view(), name='event-update'),
    url(r'event/(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='event-delete'),
    url(r'event/(?P<term>(Fa|Sp)\d{2})/$', views.TermEvents.as_view(), name='term-events'),
    # url(r'weeklyevents/create/$', views.WeeklyEventsCreate.as_view(), name='weeklyevents-create'),
    # url(r'weeklyevents/(?P<pk>\d+)/$', views.WeeklyEventsDetail.as_view(), name='weeklyevents-detail'),
]
