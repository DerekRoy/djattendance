from datetime import datetime, timedelta

from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Sum, Max, Min, Count, F

from accounts.models import Profile, Trainee, TrainingAssistant
from services.models import Service, Period
from services.constants import WORKER_ROLE_TYPES
from terms.models import Term
from teams.models import Team
from schedules.models import Event


""" SS models.py

The SS (Service Scheduler) module functions to assign services to trainees each
week.

Data Models:
    - Worker: a service worker who can fill a role on a service (e.g. trainee, short-termer, LSM hosp.)
    - WorkerGroup: a group of service workers (which can be defined by the service schedulers)
    - Instance: one specific instance of a weekly service
    - Exception: a rule exempting trainee(s) from service(s)
    - ExceptionRequest: not yet implemented
    - Qualification: a qualification a worker may have for a particular service (e.g. having a vehicle)
    - LogEvent: messages stored in the event log during scheduling (e.g. exception violation, debug messages)
    - Assignment: relates one worker to a service (with a role)
    - Schedule: a set of assignments of workers to services for a given week
    - Configuration: not yet implemented

Related Models:
    - services.Service: a weekly service recurring one per week
    - services.Category: a way to group services of similar types together (e.g. Restroom cleaning)
    - services.Period: refers to time of year this service is active (e.g. semiannual, service week, FTTA)

Abbreviations:
    sv = service
    inst = instance
"""

# Has exceptions
class Worker(models.Model):
    # Field put here so if trainee deleted will auto-delete worker model
    trainee = models.OneToOneField(Trainee)
    qualifications = models.ManyToManyField('Qualification', blank=True)
    designated = models.ManyToManyField(
        Service, related_name='designated_workers', blank=True)

    services_eligible = models.ManyToManyField(
        'Instance', related_name='workers_eligible')

    #TODO: Add in service_history, id of all prev services?, 
    # dictionary of all the types and freq

    # level from 0 to 10, 10 is healthy, 0 is dying
    health = models.PositiveIntegerField(default=10)

    workload = models.PositiveIntegerField(default=3)  #history object
    weeks = models.PositiveSmallIntegerField(default=1)  #??? what does this do?

    def _avg_workload(self):
        return self.workload / float(self.weeks)

    avg_workload = property(_avg_workload)

    def _services_exempted(self):
        # TODO: support events in the future
        exemptions = set()
        for exception in self.exceptions:
            exemptions.add(exception.services.all())
        return exemptions

    services_exempted = property(_services_exempted)

    def __unicode__(self):
        return str(self.trainee)


class WorkerGroup(Group):

    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=255)

    workers = models.ManyToManyField(
        Trainee, related_name="workergroups", blank=True)

    def __unicode__(self):
        return self.name


# You can also create one-offs instance for just this week outside of regular
# weekly services
class Instance(models.Model):
    """
    Defines one instance of a service (e.g. 6/13/14 Tuesday Breakfast Prep)
    """

    WEEKDAY = (
        ('Sun', 'Sunday'),
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
    )

    service = models.ForeignKey(Service, related_name="instances")
    # period = models.ForeignKey(Period, related_name="instances")

    date = models.DateField()

    # event created correponding to this service instance
    event = models.ForeignKey(Event, null=True, blank=True)

    workers = models.ManyToManyField(Worker, through='Assignment')

    def _start(self):
        return datetime.combine(self.date, self.service.start)
    start = property(_start)

    def _end(self):
        return datetime.combine(self.date, self.service.end)
    end = property(_end)

    def _filled(self):
        return self.workers.count() >= self.service.workers_required
    filled = property(_filled)

    def _workers_needed(self):
        return self.service.workers_required - self.workers.count()
    workers_needed = property(_workers_needed)

    def __unicode__(self):
        return str(self.date) + " " + self.service.name


class Assignment(models.Model):
    """
    Defines a relationship between a worker and a service instance
    """

    ROLES = WORKER_ROLE_TYPES

    # schedule = models.ForeignKey('Schedule')
    instance = models.ForeignKey(Instance)
    worker = models.ForeignKey(Worker)
    role = models.CharField(max_length=3, choices=ROLES, default='wor')


class Exception(models.Model):
    """
    Defines an ineligibility rule for workers to certain services.
    """

    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=255)

    start = models.DateField()
    # some exceptions are just evergreen
    end = models.DateField(null=True, blank=True)

    # whether this exception is in effect or not
    active = models.BooleanField(default=True)

    trainees = models.ManyToManyField(Worker, related_name="exceptions")
    services = models.ManyToManyField(Service)

    def checkException(self, worker, instance):
        if instance.service in self.services:
            return False
        else:
            return True

    def get_absolute_url(self):
        return "/ss/exceptions/%i/" % self.id

    def __unicode__(self):
        return self.name


class Qualification(models.Model):
    """
    Defines an eligibility for workers to certain services.
    """
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=255)

    def __unicode__(self):
        return name



class LogEvent(models.Model):

    EVENT_TYPES = (
        ('d', 'debug'),
        ('i', 'info'),
        ('w', 'warning'),
        ('e', 'error'),
    )

    schedule = models.ForeignKey('Schedule', related_name='log')

    type = models.CharField(max_length=1, choices=EVENT_TYPES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def exception_violated(cls, schedule, exception, instance, worker):
        event = cls(schedule=schedule, type='e', message="[Exception] ")
        event.message += "<a href='%s'>%s</a> violated by assigning %s to %s" % exception.get_absolute_url, exception, worker, instance
        return event

    @classmethod
    def workload_excessive(cls, schedule, worker, workload=None):
        event = cls(schedule=schedule, type='e', message="[Workload] ")
        if not workload:
            workload = worker.workload
        event.message += "%s's workload is %d" % worker, workload
        return event

    @classmethod
    def instance_unfilled(cls, schedule, instance):
        event = cls(schedule=schedule, type='w',
                    message="[Instance Not Filled] ")
        event.message = "%s still needs %s workers" % instance, instance.workers_needed

    @classmethod
    def info(cls, schedule, message):
        event = cls(schedule=schedule, type='i')
        event.message = message
        return event

    @classmethod
    def debug(cls, schedule, message):
        event = cls(schedule=schedule, type='d')
        event.message = message
        return event


class Schedule(models.Model):
    """
    A service schedule for one week in the training.
    """

    start = models.DateField()  # should be the Tuesday of every week
    desc = models.TextField()
    period = models.ForeignKey(Period)  # ???Can't we get this from start?

    # the actual schedule
    instances = models.ManyToManyField('Instance')

    # workload calculations
    workload_margin = models.PositiveSmallIntegerField(default=2)

    #TODO
    # # average workload for this schedule
    def _avg_workload(self):
        return self.instances.all().aggregate(Avg('workload')) / \
                                       Worker.objects.filter(active=True)

    avg_workload = property(_avg_workload)

    # Prevent from working way above the average trainee workload (standard of deviation)
    # avg_workload + margin = workload ceiling
    def _workload_ceiling(self):
        return self.avg_workload + self.workload_margin
    workload_ceiling = property(_workload_ceiling)

    @classmethod
    def create(cls, start, desc, period):
        schedule = cls(start=start, desc=desc, period=period)

        # create instances
        for sv in self.period.services:
            inst = Instance(service=sv, period=self.period)
            # since the week starts on Tuesday, add 6 and modulo 7 to get the
            # delta
            inst.date = self.start + \
                timedelta(days=((int(sv.weekday) + 6) % 7))
            inst.save()
            self.instances.add(inst)  # add created instance to this schedule

        return schedule

    def assign_designated_services(self):
        # assign designated services
        for dsv in self.instances.filter(service__designated=True):
            dsv.workers.add(dsv.service.designated_workers)

    def calculate_solution_space(self):
        # calculate solution space
        for worker in Worker.objects.filter(active=True):
            # clear any old eligibility data (e.g. from previous week)
            worker.services_eligible.clear()

            # if over workload ceiling, not eligible for any services, so skip
            if worker.workload >= self.workload_ceiling:
                continue

            # first assume everyone is eligible for every service
            worker.services_eligible.add(self.instances.all())

            # then remove based on exceptions
            worker.services_eligible.remove(worker.services_exempted)

            # remove based on gender
            if worker.account.gender == 'B':
                worker.services_eligible.remove(
                    self.instances.filter(service__gender='S'))
            else:
                worker.services_eligible.remove(
                    self.instances.filter(service__gender='B'))

    def assign(self, workers, instance, role='wor', commit=False):
        """ assign workers to a service instance """

        warnings = list()
        # convert to list if passed single worker
        if type(workers) is not list: workers = [workers]

        for worker in workers:
            # check worker's exceptions against instance
            for exception in worker.exceptions:
                if not exception.checkException(worker, instance):
                    warnings.append(LogEvent.exception_violated(
                        self, exception, instance, worker))

            # check worker's new workload versus workload ceiling
            if (worker.workload + instance.workload) > self.workload_ceiling:
                warnings.append(LogEvent.workload_excessive(
                    self, instance, worker, worker.workload + instance.workload))

            if commit:  # dry-run by default to preview warnings
                Assignment(instance=instance, worker=worker, role=role,
                           schedule=self).save()  # assign worker to instance
                for warning in warnings:
                    warning.save()  # write warnings to log
                # recalculate solution space
                if worker.workload > self.workload_ceiling:
                    worker.services_eligible.clear()
                else:
                    # remove same-day services
                    worker.services_eligible.remove(self.instances.filter(date=instance.date))
                worker.save()

        return warnings

    def unassign(self, worker, instance):
        """ unassign a worker from a service instance """

        # delete service assignment
        Assignment.objects.get(instance=instance, worker=worker).delete()
        # restore workload
        worker.workload -= instance.workload

        if worker.workload > self.workload_ceiling:
            worker.save()
            return  # terminate early

        # otherwise, rebuild solution space for this worker:
        # add all services again
        worker.services_eligible.add(self.instances.all())
        # then remove based on exceptions
        worker.services_eligible.remove(worker.services_exempted)
        # remove based on gender
        if worker.account.gender == 'B':
            worker.services_eligible.remove(
                self.instances.filter(service__gender='S'))
        else:
            worker.services_eligible.remove(
                self.instances.filter(service__gender='B'))

        # then simulate reassigning current services
        for inst in worker.instance_set:
            worker.services_eligible.remove(self.instances.filter(date=inst.date))


    def heuristic(self, instance, pick=1):
        """ heuristic to choose a worker from an instance's eligible workers """

        workers=instance.workers_eligible.annotate(
            num_eligible=Count('services_eligible'))

        # sort by:
        # how many services the trainee is elilgible for
        # trainee's current workload
        workers.order_by('workload', 'num_eligible')
        return workers[:pick]


    def fill(self, instances):
        """ takes a list of instances and automatically assigns workers to them """

        # yes, i know nested loops are bad.
        while not instances:
            # sorts instances by number of eligilble workers
            instance=instances.sort(
                key=lambda inst: inst.workers_eligible.count()).pop()
            while not instance.filled and instance.workers_eligible > 0:
                if instance.workers_eligible <= instance.workers_needed:
                    # assign everyone if not enough workers
                    assign(instance.workers_eligible, instance, commit=True)
                else:
                    assign(heuristic(instance, pick=1), instance, commit=True)

    def validate(self):
        """ validate this schedule, report any warnings """
        LogEvent.info(self, "beginning validation").save()

        # check instances are filled
        for instance in self.instances:
            if not instance.filled:
                LogEvent.instance_unfilled(self, instance)
            else:
                continue

        for worker in Workers.objects.filter(active=True):
            # check each workers assignments against exceptions
            if worker.services_exempted and worker.assignment_set.filter(schedule=self).values('service'):
                pass
                # issue exception warnings

            # check workload ceilings
            if worker.workload > self.workload_ceiling:
                LogEvent.workload_excessive(self, worker).save()

    def finalize(self):
        Workers.objects.filter(active=True).update(weeks=F('weeks') + 1)
        self.validate()
