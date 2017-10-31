from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from accounts.models import Trainee
from houses.models import House


class Command(BaseCommand):

  def _assign_houses(self):
    first_names = ['Enoch', 'Samuel']
    trainees = Trainee.objects.filter(firstname__in=first_names)
    house = House.objects.get(name="2105 Grace Ct.")
    group = Group.objects.get(name='HC')
    for trainee in trainees:
      trainee.house = house
      trainee.save()
      print "%s assigned to %s" % (trainee, house)
      if trainee.firstname == 'Enoch':
        group.user_set.add(trainee)
        print "%s assigned as %s" % (trainee, group)

  def handle(self, *args, **options):
    print("* Assigning houses and HCs")
    self._assign_houses()
