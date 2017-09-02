from django.db import models

'''
Service swap -> check qualification mismatch but maybe lax on schedule conflict exception checking
'''

class Assignment(models.Model):
  """
  Defines a relationship between a worker and a service instance
  """

  week_schedule = models.ForeignKey('WeekSchedule', related_name='assignments')

  service = models.ForeignKey('Service', related_name='assignments')
  # Get role + workload
  service_slot = models.ForeignKey('ServiceSlot', related_name='assignments', default=None)

  workers = models.ManyToManyField('Worker', related_name="assignments", blank=True)

  @property
  def workers_needed(self):
    return self.service_slot.workers_required - self.workers.count()

  def get_worker_list(self):
    return ', '.join([w.trainee.full_name for w in self.workers.all()])

  # boolean determines if assignment made should be pinned, not altered by
  # flow algo, taken out of graph, trainee need services decremented (safest way to do it)
  # Maybe cost of edge 0?
  pin = models.BooleanField(default=False)

  # For AV/Piano, workload would be 0, no effect on services needed
  # For Shuttle, could be 1 as real service
  workload = models.PositiveSmallIntegerField(default=1)

  last_modified = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return '%s assignment for %s' % (self.service, self.week_schedule)

  @staticmethod
  def get_assignments_to_worker(worker):
    return Assignment.objects.filter(workers=worker).all()

  def worker_list(self):
    return ', '.join([w.trainee.full_name for w in self.workers.all()])
