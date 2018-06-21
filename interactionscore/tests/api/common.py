import pytest
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


from interactionscore.management.commands.setup_user_roles import (
    Command as SetupUserRolesCommand
)
from interactionscore.models import (
    AffiliateGroup,
    HCP,
    EngagementPlan,
    Interaction,
    Project,
    InteractionOutcome,
    Resource,
    TherapeuticArea,
)


User = get_user_model()


@pytest.mark.django_db
class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # setup default user roles and permissions
        SetupUserRolesCommand().handle(delete_old_groups=False,
                                       delete_old_permissions=False,
                                       create_new_permissions=False)

        # therapeutic areas
        cls.ta1 = TherapeuticArea.objects.create(name='TA 1')
        cls.ta2 = TherapeuticArea.objects.create(name='TA 2')
        cls.ta3 = TherapeuticArea.objects.create(name='TA 3')

        # affiliate groups
        cls.ag1 = AffiliateGroup.objects.create(name='Affiliate Group 1')
        cls.ag2 = AffiliateGroup.objects.create(name='Affiliate Group 2')

        # create users
        cls.superuser = User.objects.create_superuser(
            email='superuser@test.com', password='secret')
        group_msl = Group.objects.get(name='Role MSL')
        group_man = Group.objects.get(name='Role MSL Manager')

        cls.user_msl1 = User.objects.create(email='msl.1@test.com', password='secret')
        cls.user_msl1.affiliate_groups.set([cls.ag1])
        group_msl.user_set.add(cls.user_msl1)

        cls.user_msl2 = User.objects.create(email='msl.2@test.com', password='secret')
        cls.user_msl2.affiliate_groups.set([cls.ag1, cls.ag2])
        group_msl.user_set.add(cls.user_msl2)

        cls.user_msl3 = User.objects.create(email='msl.3@test.com', password='secret')
        cls.user_msl3.affiliate_groups.set([cls.ag2])
        group_msl.user_set.add(cls.user_msl3)

        cls.user_man1 = User.objects.create(email='man.1@test.com', password='secret')
        cls.user_man1.affiliate_groups.set([cls.ag1])
        group_man.user_set.add(cls.user_man1)

        cls.user_man2 = User.objects.create(email='man.2@test.com', password='secret')
        cls.user_man2.affiliate_groups.set([cls.ag1, cls.ag2])
        group_man.user_set.add(cls.user_man2)

        cls.user_man3 = User.objects.create(email='man.3@test.com', password='secret')
        cls.user_man3.affiliate_groups.set([cls.ag2])
        group_man.user_set.add(cls.user_man3)

        cls.hcp1 = HCP.objects.create(email='hcp.1@test.com')
        cls.hcp2 = HCP.objects.create(email='hcp.2@test.com')
        cls.hcp3 = HCP.objects.create(email='hcp.3@test.com')

        # engagement plan
        cls.ep1 = EngagementPlan.objects.create(
            user=cls.user_msl1,
            year='2017-01-01'
        )
        cls.ep1.engagement_list_items.create(hcp=cls.hcp1)
        cls.ep1.engagement_list_items.create(hcp=cls.hcp2)
        cls.ep1.engagement_list_items.create(hcp=cls.hcp3)
        ep1_obj1 = cls.ep1.hcp_objectives.create(hcp=cls.hcp1,
                                                 description='hcp 1 obj desc')
        ep1_obj1.deliverables.create(quarter=1, description='q1 desc')
        ep1_obj1.deliverables.create(quarter=2, description='q2 desc')
        ep1_obj1.deliverables.create(quarter=3, description='q3 desc')

        cls.ep1 = EngagementPlan.objects.create(
            user=cls.user_msl2,
            year='2018-01-01'
        )
        cls.ep1.engagement_list_items.create(hcp=cls.hcp1)
        cls.ep1.engagement_list_items.create(hcp=cls.hcp2)
        cls.ep1.engagement_list_items.create(hcp=cls.hcp3)
        ep1_obj1 = cls.ep1.hcp_objectives.create(hcp=cls.hcp1,
                                                  description='hcp 1 obj desc')
        ep1_obj1.deliverables.create(quarter=1, description='q1 desc')
        ep1_obj1.deliverables.create(quarter=2, description='q2 desc')
        ep1_obj1.deliverables.create(quarter=3, description='q3 desc')

        # projects
        cls.proj1 = Project.objects.create(name='project 1')
        cls.proj2 = Project.objects.create(name='project 2')

        # resources
        cls.res1 = Resource.objects.create(url='http://www.test.com/res1.pdf')
        cls.res2 = Resource.objects.create(url='http://www.test.org/file2.zip')

        # interaction outcomes
        cls.iout1 = InteractionOutcome.objects.create(name='outcome 1')
        cls.iout2 = InteractionOutcome.objects.create(name='outcome 2')

        # interaction
        cls.inter1 = Interaction.objects.create(
            user=cls.user_msl1,
            hcp=cls.hcp1,
            description='first interaction between MSL1 and HCP1',
        )

