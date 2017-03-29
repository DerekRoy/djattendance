from django.db import models


# TODO: UI represent as time blocks -> translate into services blocked out
# TODO: Should exceptions handle time block conflict checking in addition
# to just service blocking?
class Exception(models.Model):
    """
    Defines an ineligibility rule for workers to certain services.
    """

    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=255, null=True, blank=True)

    # Tag allows for custom filtering and tagging of big exception data set
    tag = models.CharField(max_length=255, null=True, blank=True)

    start = models.DateField()
    # some exceptions are just evergreen
    # UI will give 3 options, definite date (should be end of working week), end of term, permanent (empty)
    end = models.DateField(null=True, blank=True)

    # whether this exception is in effect or not
    active = models.BooleanField(default=True)

    workers = models.ManyToManyField('Worker', related_name="exceptions")
    services = models.ManyToManyField('Service', related_name='exceptions')
    # If none chosen, apply to all schedules by default
    schedule = models.ForeignKey('SeasonalServiceSchedule', related_name='exceptions', null=True, blank=True, verbose_name='Restrict to schedule (leave blank to apply to all)')

    workload = models.PositiveSmallIntegerField(default=0)

    # Designated service
    service = models.ForeignKey('Service', related_name='service_exceptions', null=True, blank=True)

    last_modified = models.DateTimeField(auto_now=True)

    def get_worker_list(self):
        return ','.join([w.trainee.full_name for w in self.workers.all()])

    def checkException(self, worker, instance):
        if instance.service in self.services:
            return False
        else:
            return True

    def get_absolute_url(self):
        return "/ss/exceptions/%i/" % self.id

    def __unicode__(self):
        return self.name


# TODO: ExceptionRequest (request for exception to be added instead of a handwritten note to schedulers)