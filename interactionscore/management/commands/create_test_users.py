from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


from interactionscore.models import AffiliateGroup, TherapeuticArea


User = get_user_model()


USERS_DATA = [
    {'email': 'msl.1@test.com',
     'groups': ['Role MSL']},
    {'email': 'msl.2@test.com',
     'groups': ['Role MSL']},
    {'email': 'msl.3@test.com',
     'groups': ['Role MSL']},
    {'email': 'man.a@test.com',
     'groups': ['Role MSL Manager']},
    {'email': 'man.b@test.com',
     'groups': ['Role MSL Manager']},
    {'email': 'man.c@test.com',
     'groups': ['Role MSL Manager']},
]


class Command(BaseCommand):
    help = 'Create test users'

    def handle(self, *args, **options):
        self.create_test_users(USERS_DATA)
        self.stdout.write(self.style.SUCCESS('...done!'))

    def create_test_users(self, users_data):
        for data in users_data:
            group_names = data.pop('groups', [])
            tas = data.pop('tas', [])
            affiliate_groups = data.pop('affiliate_groups', [])

            user = User.objects.create_user(**data)
            self.stdout.write("Created user {}".format(data['email']))

            for group_name in group_names:
                group = Group.objects.get(name=group_name)
                group.user_set.add(user)
                self.stdout.write('- added user {} to group: {}'.format(
                    data['email'], group_name))

            user.affiliate_groups.set([
                AffiliateGroup.objects.get(name=name)
                for name in affiliate_groups
            ])
            self.stdout.write('- added user {} to Affiliate Groups: {}'.format(
                data['email'], ', '.join(affiliate_groups))
            )

            user.tas.set([
                TherapeuticArea.objects.get(name=name)
                for name in tas
            ])
            self.stdout.write('- added user {} to Therapeutic Areas: {}'.format(
                data['email'], ', '.join(affiliate_groups))
            )
