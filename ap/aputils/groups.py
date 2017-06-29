from django.conf import settings

# Adds all the permissions for the listed models
def model_permissions(group, model_name_list):
  import django; django.setup()
  from django.contrib.contenttypes.models import ContentType
  from django.contrib.auth.models import Group, Permission
  for model_name in model_name_list:
    ct = ContentType.objects.get(model=model_name)
    permission_list = Permission.objects.filter(content_type=ct)
    for permission in permission_list:
      group.permissions.add(permission)

# Adds all the permissions for the listed apps
# Locks down all the models in listed apps to specific group
def add_permissions(group, app_label_list):
  import django; django.setup()
  from django.contrib.contenttypes.models import ContentType
  from django.contrib.auth.models import Group, Permission
  for app_label in app_label_list:
    cts = ContentType.objects.filter(app_label=app_label)
    for ct in cts:
      permission_list = Permission.objects.filter(content_type=ct)
      for permission in permission_list:
        group.permissions.add(permission)

def add_group_permissions(sender, **kwargs):
  import django; django.setup()
  from django.contrib.contenttypes.models import ContentType
  from django.contrib.auth.models import Group, Permission
  print 'Populating Permission Groups...'

  group_set = set(Group.objects.all())

  # Update permissions
  APPS = list(settings.APPS)

  group_list = [
    ('administration', APPS),
    ('maintenance', ['house_requests']),
    ('absent_trainee_roster', ['absent_trainee_roster']),
    ('attendance_monitors', ['attendance', 'seating', 'schedules', 'leaveslips']),
    ('av', []),
    ('dev', APPS),
    ('networks', []),
    ('exam_graders', ['exams']),
    ('grad_committee', []),
    ('HC', ['house_requests']),
    ('facility_maintenance_or_frames_or_linens', ['house_requests']),
    ('house_inspectors', []),
    ('semi_annual_testing_group_coordinators', []),
    ('service_schedulers', ['services']),
    ('team_monitors', ['attendance']),
    ('ypc_monitors', ['attendance']),
    ('xb_trainees', []),
    ('designated_service', []),
    ('special_projects', []),
    ('office_support', []),
    ('badges', ['badges']),
    ('health_office', []),
    ('kitchen', ['meal_seating'])
  ]

  # Add predefined permissions if not in db already
  for g, p_list in group_list:
    group, created = Group.objects.get_or_create(name=g)
    if created:
      print 'Added Group', group
    if group in group_set:
      group_set.remove(group)
    # For now permissions is to lock down django admin.
    # Views should preferably use groups for access permissions
    add_permissions(group, p_list)

  # Delete any groups in db not declared explicitly here
  for p in group_set:
    p.delete()
    print 'Deleted Group', p

  print 'Groups updated.'
