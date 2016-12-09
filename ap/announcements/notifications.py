import datetime

from django.contrib import messages
from django.db.models import Count, Q
from django.core.urlresolvers import reverse

from models import Announcement
from bible_tracker.models import BibleReading
from leaveslips.models import IndividualSlip, GroupSlip
from web_access.models import WebRequest
from terms.models import Term
from aputils.trainee_utils import is_trainee, trainee_from_user

def get_announcements(request):
    notifications = []
    if is_trainee(request.user):
        trainee = trainee_from_user(request.user)
        notifications.extend(discipline_announcements(trainee))
        notifications.extend(server_announcements(trainee))
        notifications.extend(bible_reading_announcements(trainee))
        notifications.extend(request_statuses(trainee))
    return notifications

def request_statuses(trainee):
    requests = []
    requests.extend(IndividualSlip.objects.filter(trainee=trainee, status='F'))
    requests.extend(GroupSlip.objects.filter(trainee=trainee, status='F'))
    requests.extend(WebRequest.objects.filter(trainee=trainee, status='F'))
    requests.extend(Announcement.objects.filter(trainee=trainee, status='F'))
    print(requests)
    return [(messages.WARNING, 'Your <a href="{url}">{request}</a> has been marked for fellowship'.format(url=req.get_absolute_url(), request=req._meta.verbose_name)) for req in requests]

def bible_reading_announcements(trainee):
    term = Term.current_term()
    week = term.term_week_of_date(datetime.date.today())
    url = reverse('bible_tracker:index')
    try:
        reading = BibleReading.objects.get(trainee=trainee)
    except:
        return [(messages.WARNING, 'You have not filled out your <a href="{url}">Bible reading</a>'.format(url=url))]
    notifications = []
    for w in range(week):
        stats = reading.weekly_statistics(w, w, term.id)
        if stats['number_filled'] < 7:
            notifications.append((messages.WARNING, 'You have not filled out your <a href="{url}">Bible reading</a> for week {week} yet'.format(url=url, week=w)))
    return notifications

def server_announcements(trainee):
    today = datetime.date.today()
    announcements = Announcement.objects \
        .annotate(num_trainees=Count('trainees')) \
        .filter(Q(type='SERVE',
            status='A',
            announcement_date__lte=today,
            announcement_end_date__gte=today
        ) & (Q(num_trainees=0) | Q(trainees=trainee)))
    return [(messages.INFO, a.announcement) for a in announcements]

def discipline_announcements(trainee):
    notifications = []
    url = reverse('lifestudies:discipline_list')
    for discipline in trainee.discipline_set.all():
        if discipline.get_num_summary_due() > 0:
            content = 'Life Study Summary due for {infraction}. <a href="{url}">Still need: {due}</a>'.format(infraction=discipline.get_infraction_display(), url=url, due=discipline.get_num_summary_due())
            notifications.append((messages.WARNING, content))
    return notifications
