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

        # projects
        cls.proj1 = Project.objects.create(name='project 1')
        cls.proj2 = Project.objects.create(name='project 2')
        cls.proj2 = Project.objects.create(name='project 3')

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

        # engagement plans
        #################################################

        # EP1
        cls.ep1 = EngagementPlan.objects.create(
            user=cls.user_msl1,
            year='2018-01-01'
        )
        # HCP items
        ep1_hcp_item1 = cls.ep1.hcp_items.create(hcp=cls.hcp1)
        ep1_hcp_item1_obj1 = ep1_hcp_item1.objectives.create(
            hcp=cls.hcp1, description='hcp 1 obj 1 desc')
        ep1_hcp_item1_obj1.deliverables.create(quarter=1, description='q1 deliverable desc')
        ep1_hcp_item1_obj1.deliverables.create(quarter=2, description='q2 deliverable desc')
        ep1_hcp_item1_obj1.deliverables.create(quarter=3, description='q3 deliverable desc')
        ep1_hcp_item1_obj2 = ep1_hcp_item1.objectives.create(
            hcp=cls.hcp1, description='hcp 1 obj 2 desc')
        ep1_hcp_item1_obj2.deliverables.create(quarter=1, description='q1 deliverable desc')
        ep1_hcp_item1_obj2.deliverables.create(quarter=2, description='q2 deliverable desc')
        ep1_hcp_item1_obj2.deliverables.create(quarter=3, description='q3 deliverable desc')
        ep1_hcp_item1_obj2.deliverables.create(quarter=4, description='q4 deliverable desc')
        ep1_hcp_item2 = cls.ep1.hcp_items.create(hcp=cls.hcp2)
        ep1_hcp_item2_obj = ep1_hcp_item2.objectives.create(
            hcp=cls.hcp2, description='hcp 2 obj desc')
        ep1_hcp_item2_obj.deliverables.create(quarter=2, description='q2 deliverable desc')
        ep1_hcp_item2_obj.deliverables.create(quarter=3, description='q3 deliverable desc')
        # Project items
        ep1_proj_item1 = cls.ep1.project_items.create(project=cls.proj1)
        ep1_proj_item1_obj1 = ep1_proj_item1.objectives.create(
            project=cls.proj1, description='proj 1 obj 1 desc')
        ep1_proj_item1_obj1.deliverables.create(quarter=1, description='q1 deliverable desc')
        ep1_proj_item1_obj1.deliverables.create(quarter=2, description='q2 deliverable desc')
        ep1_proj_item1_obj1.deliverables.create(quarter=3, description='q3 deliverable desc')
        ep1_proj_item1_obj2 = ep1_proj_item1.objectives.create(
            project=cls.proj1, description='proj 1 obj 2 desc')
        ep1_proj_item1_obj2.deliverables.create(quarter=1, description='q1 deliverable desc')
        ep1_proj_item1_obj2.deliverables.create(quarter=2, description='q2 deliverable desc')
        ep1_proj_item1_obj2.deliverables.create(quarter=3, description='q3 deliverable desc')
        ep1_proj_item1_obj2.deliverables.create(quarter=4, description='q4 deliverable desc')
        ep1_proj_item2 = cls.ep1.project_items.create(project=cls.proj2)
        ep1_proj_item2_obj = ep1_proj_item2.objectives.create(
            project=cls.proj1, description='proj 2 obj desc')
        ep1_proj_item2_obj.deliverables.create(quarter=2, description='q2 deliverable desc')
        ep1_proj_item2_obj.deliverables.create(quarter=3, description='q3 deliverable desc')

        #
        # cls.ep2 = EngagementPlan.objects.create(
        #     user=cls.user_msl2,
        #     year='2018-01-01'
        # )
        # cls.ep2.engagement_list_items.create(hcp=cls.hcp1)
        # cls.ep2.engagement_list_items.create(hcp=cls.hcp2)
        # ep2_obj1 = cls.ep2.hcp_objectives.create(hcp=cls.hcp1,
        #                                          description='hcp 1 obj desc')
        # ep2_obj1.deliverables.create(quarter=1, description='q1 desc')
        # ep2_obj1.deliverables.create(quarter=2, description='q2 desc')
        # ep2_obj1.deliverables.create(quarter=3, description='q3 desc')

        # resources
        cls.res1 = Resource.objects.create(url='http://www.test.com/res1.pdf')
        cls.res2 = Resource.objects.create(url='http://www.test.org/file2.zip')
        cls.res3 = Resource.objects.create(url='http://www.test.co.uk/imh3/jpg')

        # interaction outcomes
        cls.iout1 = InteractionOutcome.objects.create(name='outcome 1')
        cls.iout2 = InteractionOutcome.objects.create(name='outcome 2')
        cls.iout3 = InteractionOutcome.objects.create(name='outcome 3')

        # interactions
        cls.inter1 = Interaction.objects.create(
            user=cls.user_msl1,
            hcp=cls.hcp1,
            project=cls.proj1,
            description='first interaction between MSL1 and HCP1',
        )
        cls.inter1.resources.set([cls.res1])
        cls.inter1.outcomes.set([cls.iout3])
