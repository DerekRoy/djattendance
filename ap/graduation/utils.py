from aputils.trainee_utils import is_trainee
from graduation.models import Testimony, Consideration, Website, Outline, Misc, GradAdmin
from terms.models import Term


def grad_forms(user):
  forms = []
  if is_trainee(user):

    admin, created = GradAdmin.objects.get_or_create(term=Term.current_term())
    models = [Testimony, Consideration, Website, Outline, Misc]
    for m in models:
      forms.append(m.objects.get_or_create(trainee=user, grad_admin=admin)[0])

    forms = filter(lambda f: (user.current_term == 4 and f.show_status != 'NO'), forms)

  return forms
