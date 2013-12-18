import random

from accounts.models import User, TrainingAssistant, Trainee
from aputils.models import Address
from autofixture import generators, register, AutoFixture
from houses.models import House, Bunk
from teams.models import Team
from terms.models import Term
import datetime

""" accounts.autofixtures

Uses django-autofixture to generate random testing data.
(https://github.com/gregmuellegger/django-autofixture/)

Create test data using the loadtestdata command, for example:
$ django-admin.py loadtestdata accounts.User:50 accounts.TrainingAssistant:5 accounts.Trainee:50

(note: generate Users before generating TAs and Trainees)
"""

class AsianNameGenerator(generators.Generator):
    """
    Generates a random, generic, monosyllabic Asian name.
    AUTHOR'S NOTE: This class is not critical for autofixtures, but was created
    to generate gender-neutral names.  The name bank was created by combing
    through the Fall 2013 roster and choosing all the monosyllabic Asian last
    names.
    """

    names = [
        "Ahn", "Baek", "Bai", "Bang", "Bong", "Chai", "Chang", "Chao", "Chen",
        "Chern", "Cheung", "Chi", "Chiang", "Chiu", "Choi", "Chou", "Chiu",
        "Chu", "Chuah", "Chuang", "Co", "Ding", "Duong", "Feng", "Fok", "Han",
        "Harm", "He", "Hsieh", "Hsiung", "Hsu", "Hu", "Hua", "Huang", "Hung",
        "Hwang", "Jahng", "Jeng", "Jiao", "Jiang", "Jin", "Jou", "Jung", "Kan",
        "Kao", "Kim", "Kor", "Kuo", "Lan", "Lee", "Leung", "Li", "Liang",
        "Lie", "Lim", "Lin", "Liou", "Liu", "Loke", "Lu", "Luo", "Luor", "Mai",
        "Mok", "Pan", "Park", "Peng", "Perng", "Po", "Qin", "Qu", "Ser",
        "Shao", "Shi", "Tai", "Tak", "Tan", "Tien", "Tsai", "Tsang", "Ung",
        "Wang", "Wei", "Wong", "Wu", "Xie", "Xu", "Xue", "Yan", "Yang", "Yao",
        "Ye", "Yen", "Young", "Yu", "Zhan", "Zheng", "Zhou", "Zhu", "Zou"
    ]

    def generate(self):
        return random.choice(self.names)


class UserAutoFixture(AutoFixture):
    # This sets the ratios of the genders
    gender_ratios = [(generators.StaticGenerator("B"), 45),
                     (generators.StaticGenerator("S"), 55)]
    # Arbitrarily have each trainee aged 20 years old
    birthdate = datetime.date.today() - datetime.timedelta(365 * 20)
    field_values = {
        'email': generators.EmailGenerator(static_domain='ftta.org'),
        'firstname': AsianNameGenerator(),
        'lastname': AsianNameGenerator(),
        'middlename': generators.StaticGenerator(''),
        'nickname': generators.StaticGenerator(''),
        'maidenname': generators.StaticGenerator(''),
        'gender': generators.WeightedGenerator(choices=gender_ratios),
        'date_of_birth': birthdate,
    }

register(User, UserAutoFixture)


class CampusTeamGenerator(generators.Generator):
    """
    Generates a campus team.
    """

    def generate(self):
        team = Team()
        team.name, team.type = 'CalStateLA Team', 'CAMPUS'
        return team


class ChildrensTeamGenerator(generators.Generator):
    """
    Generates a children's team.
    """

    def generate(self):
        team = Team()
        team.name, team.type = 'Children\'s Team', 'CHILD'
        return team


class CommunityTeamGenerator(generators.Generator):
    """
    Generates a community team.
    """

    def generate(self):
        team = Team()
        team.name, team.type = 'Anaheim Community Team', 'COM'
        return team


class YPTeamGenerator(generators.Generator):
    """
    Generates a YP team.
    """

    def generate(self):
        team = Team()
        team.name, team.type = 'Anaheim YP Team', 'YP'
        return team


class InternetTeamGenerator(generators.Generator):
    """
    Generates an Internet team.
    """

    def generate(self):
        team = Team()
        team.name, team.type = 'I-DCP Team', 'I'
        return team


class TraineeAutoFixture(AutoFixture):
    # This sets the ratios of the trainee types ('R' is for regular trainees,
    # C' is for commuter trainees, and 'S' is for long term short term
    # trainees)
    trainee_type_ratios = [(generators.StaticGenerator('R'), 70),
                           (generators.StaticGenerator('C'), 30)]
    # Generate teams
    teams = Team.objects.all()
    if not teams:
        team = Team()
        team.name = 'Children\'s Team'
        team.type = 'CHILD'
    else:
        team = teams[0]
    # Generate dummy fields for trainees
    term = Term()
    date_begin = datetime.date.today()
    date_end = datetime.date.today()
    ta = TrainingAssistant()
    mentor = Trainee()
    house = House()
    bunk = Bunk()
    address = Address()
    spouse = Trainee()
    field_values = {
        'type': generators.WeightedGenerator(choices=trainee_type_ratios),
        'date_begin': date_begin,
        'date_end': date_end,
        'ta': ta,
        'mentor': mentor,
        'team': team,
        'house': house,
        'bunk': bunk,
        'address': address,
        'spouse': spouse
    }

register(Trainee, TraineeAutoFixture)