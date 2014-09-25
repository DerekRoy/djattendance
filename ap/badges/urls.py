from django.conf.urls import patterns,url
from . import views
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = patterns(
    '',
    url(r'^$', views.BadgeListView.as_view(), name='badges_list'),
    url(r'^print/$', 'badges.views.badgeprintout', name='badges_print'),
    url(r'^print/term/front/$', views.BadgePrintFrontView.as_view(), name='badges_print_term_front'),
    url(r'^print/term/back/$', views.BadgePrintBackView.as_view(), name='badges_print_term_back'),
    url(r'^print/back/$', views.BadgePrintGeneralBackView.as_view(), name='badges_print_general_back'),
    url(r'^print/term/facebook/$', views.BadgePrintFacebookView.as_view(), name='badges_print_term_facebook'),
    url(r'^print/staff/$', views.BadgePrintStaffView.as_view(), name='badges_print_staff'),
    url(r'^print/shortterm/$', views.BadgePrintShorttermView.as_view(), name='badges_print_shortterm'),
    url(r'^print/usher/$', views.BadgePrintUsherView.as_view(), name='badges_print_usher'),
    url(r'^print/temp/$', views.BadgePrintTempView.as_view(), name='badges_print_temp'),
    url(r'^print/visitor/$', views.BadgePrintVisitorView.as_view(), name='badges_print_visitor'),
    url(r'^print/office/$', views.BadgePrintOfficeView.as_view(), name='badges_print_office'),
    url(r'^create/$', views.BadgeCreateView.as_view(), name='badge_create'),
    url(r'^edit/(?P<pk>\d+)/$', views.BadgeUpdateView.as_view(), name='badge_detail'),
    url(r'^delete/(?P<pk>\d+)/$', views.BadgeDeleteView.as_view(), name='badge_delete'),
    url(r'^create/batch/$', 'badges.views.batch', name='badges_batch'),
    url(r'^view/(?P<term>(Fa|Sp)\d{2})/$', views.BadgeTermView.as_view(), name='badges_term'),
    url(r'^view/xb/(?P<term>(Fa|Sp)\d{2})/$', views.BadgeXBTermView.as_view(), name='badges_term_xb'),
    url(r'^view/staff/$', views.BadgeStaffView.as_view(), name='badges_staff'),
    url(r'^print/term/facebook/generate/$', 'badges.views.genpdf', name='badges_print_term_genpdf'),
) 