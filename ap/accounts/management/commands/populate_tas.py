from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    # to use: python ap/manage.py populate_tas --settings=ap.settings.dev
    def _create_tas(self):
        # change the array below to get different tas
        tas = ['Andrew Li', 'Jerome Keh', 'Joseph Bang', 'Paul Deng', 'Walt Hale', 'Joe Prim']
        sister_tas = ['Nikki Miao', 'Veronica Montoya', 'Hannah Chumreonlert', 'Raizel Macaranas', 'Ann Buntain', 'Annie Uy']
        for ta in tas:
            print ta
            email = '.'.join(ta.lower().split(' ')) + "@lsm.org"
            firstname = ta.split(' ')[0]
            lastname = ta.split(' ')[1]
            gender = 'B'
            password = 'ap'
            date_of_birth = '1974-12-12'
            u = User(email=email, firstname=firstname, lastname=lastname, gender=gender, password=password, type='T', date_of_birth=date_of_birth, is_staff=True, is_admin=True)
            u.save()

        for ta in sister_tas:
            print ta
            email = '.'.join(ta.lower().split(' ')) + "@lsm.org"
            firstname = ta.split(' ')[0]
            lastname = ta.split(' ')[1]
            gender = 'S'
            password = 'ap'
            date_of_birth = '1974-12-12'
            u = User(email=email, firstname=firstname, lastname=lastname, gender=gender, password=password, type='T', date_of_birth=date_of_birth, is_staff=True, is_admin=True)
            u.save()

        print 'done'

    def handle(self, *args, **options):
        self._create_tas()