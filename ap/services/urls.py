from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  url(r'^$', views.services_view, name='services_view'),
  url(r'^assign$', views.services_view, {'run_assign': True}, name='services_assign_view'),
  url(r'^generate_leaveslips$', views.services_view, {'generate_leaveslips': True}, name='services_generate_leaveslips'),
  url(r'^generate_schedule_house$', views.generate_report, {'house': True}, name='services_schedule_house'),
  url(r'^generate_schedule$', views.generate_report, name='services_schedule'),
  url(r'^generate_signinr$', views.generate_signin, {'r': True}, name='rservices_signin'),
  url(r'^generate_signink$', views.generate_signin, {'k': True}, name='kservices_signin'),
  url(r'^generate_signino$', views.generate_signin, {'o': True}, name='oservices_signin'),
  url(r'^designated_service_hours$', views.ServiceHours.as_view(), name='services_schedule'),
]
