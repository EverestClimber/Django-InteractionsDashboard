import pytest
import pprint
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from interactionscore.management.commands.setup_user_roles import Command as SetupUserRolesCommand
from interactionscore.models import (
    AffiliateGroup,
    HCP,
    EngagementPlan,
)

pp = pprint.PrettyPrinter(indent=2).pprint
User = get_user_model()


def print_json(label, data):
    print("\n=== {}:".format(label),
          json.dumps(data, indent=2),
          "\n=== /{}\n".format(label))


@pytest.mark.django_db
class TestEngagementPlansAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        SetupUserRolesCommand().handle(delete_old_groups=False,
                                       delete_old_permissions=False,
                                       create_new_permissions=False)

        cls.ag1 = AffiliateGroup.objects.create(name='Affiliate Group 1')
        cls.ag2 = AffiliateGroup.objects.create(name='Affiliate Group 2')

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

    def setUp(self):
        self.client.force_login(self.user_msl1)

        self.ep1 = EngagementPlan.objects.create(
            user=self.user_msl1,
            year='2018-01-01'
        )
        self.ep1.engagement_list_items.create(hcp=self.hcp1)
        self.ep1.engagement_list_items.create(hcp=self.hcp2)
        self.ep1.engagement_list_items.create(hcp=self.hcp3)
        ep1_obj1 = self.ep1.hcp_objectives.create(hcp=self.hcp1,
                                                  description='hcp 1 obj desc')
        ep1_obj1.deliverables.create(quarter=1, description='q1 desc')
        ep1_obj1.deliverables.create(quarter=2, description='q2 desc')
        ep1_obj1.deliverables.create(quarter=3, description='q3 desc')

        self.ep1 = EngagementPlan.objects.create(
            user=self.user_msl2,
            year='2018-01-01'
        )
        self.ep1.engagement_list_items.create(hcp=self.hcp1)
        self.ep1.engagement_list_items.create(hcp=self.hcp2)
        self.ep1.engagement_list_items.create(hcp=self.hcp3)
        ep1_obj1 = self.ep1.hcp_objectives.create(hcp=self.hcp1,
                                                  description='hcp 1 obj desc')
        ep1_obj1.deliverables.create(quarter=1, description='q1 desc')
        ep1_obj1.deliverables.create(quarter=2, description='q2 desc')
        ep1_obj1.deliverables.create(quarter=3, description='q3 desc')

    def test_list_engagement_plans(self):
        url = reverse('engagementplan-list')
        res = self.client.get(url)
        print_json('res', res.json())
        assert res.status_code == status.HTTP_200_OK
        rdata = res.json()

        assert len(rdata) == 2  # just one bc other belongs to msl2

        # no eps of other msls
        assert sum(ep['user_id'] != self.user_msl1.id for ep in rdata) == 0
