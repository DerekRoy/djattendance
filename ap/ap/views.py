from django.contrib.auth.views import login as django_login
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from dailybread.models import Portion
from schedules.models import Schedule
from terms.models import Term
from accounts.models import Trainee
from web_access import utils
from web_access.models import WebRequest
from web_access.forms import WebAccessRequestGuestCreateForm


from aputils.utils import is_trainee, is_TA, trainee_from_user

@login_required
def home(request):
    data = {'daily_nourishment': Portion.today(),
            'user': request.user}

    if is_trainee(request.user):
        trainee = trainee_from_user(request.user)
        try:
            data['schedules'] = trainee.schedules.filter(season=trainee.current_season)
        except ObjectDoesNotExist:
            pass
        for discipline in trainee.discipline_set.all():
            if discipline.get_num_summary_due() > 0:
                messages.warning(request, 'Life Study Summary Due for {infraction}. <a href="/lifestudies">Still need: {due}</a>'.format(infraction=discipline.get_infraction_display(), due=discipline.get_num_summary_due()))

    elif is_TA(request.user):
        #do stuff to TA
        pass
    else:
        #do stuff to other kinds of users
        pass

    return render(request, 'index.html', dictionary=data)


def base_example(request):
    return render(request, 'base_example.html')


def login(request):
    """ Adds web access requests for guests to login page """
    form = WebAccessRequestGuestCreateForm(request.POST or None)
    mac = utils._getMAC(utils._getIPAddress(request))
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.mac_address = mac
        instance.save()
        messages.add_message(request, messages.SUCCESS, "Submitted guest web access request.")

    objects = WebRequest.objects.all().filter(trainee=None, mac_address=mac).order_by('status')
    return django_login(request, extra_context={'webaccess_form': form, 'guest_access_requests': objects})
