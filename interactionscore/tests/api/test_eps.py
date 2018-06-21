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


def get_item(target_list, field, value):
    r = [it for it in target_list if it[field] == value]
    assert len(r) == 1
    return r[0]


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
            year='2017-01-01'
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

        assert len(rdata) == 1  # just one bc other belongs to msl2

        # no eps of other msls
        assert sum(ep['user_id'] != self.user_msl1.id for ep in rdata) == 0

    def test_create_engagement_plan(self):
        url = reverse('engagementplan-list')
        data = {
            "year": "2018-01-01",
            "engagement_list_items": [
                {"hcp_id": self.hcp1.id},
                {"hcp_id": self.hcp2.id}
            ],
            "hcp_objectives": [
                {"hcp_id": self.hcp1.id,
                 "description": "objective of hcp #1",
                 "deliverables": [
                     {"quarter": 1, "description": "q1 hcp1 deliverable desc"},
                     {"quarter": 2, "description": "q2 hcp1 deliverable desc"},
                     {"quarter": 3, "description": "q3 hcp1 deliverable desc"},
                 ]},
                {"hcp_id": self.hcp2.id,
                 "description": "objective 1 of hcp #2",
                 "deliverables": [
                     {"quarter": 1, "description": "q1 hcp2 obj1 deliverable desc"},
                     {"quarter": 2, "description": "q2 hcp2 obj1 eliverable desc"},
                     {"quarter": 3, "description": "q3 hcp2 obj1 deliverable desc"},
                 ]},
                {"hcp_id": self.hcp2.id,
                 "description": "objective 2 of hcp #2",
                 "deliverables": [
                     {"quarter": 1, "description": "q1 hcp2 obj2 deliverable desc"},
                     {"quarter": 2, "description": "q2 hcp2 obj2 deliverable desc"},
                     {"quarter": 3, "description": "q3 hcp2 obj2 deliverable desc"},
                 ]},
            ]
        }
        res = self.client.post(url, data)
        print_json('res', res.json())
        assert res.status_code == status.HTTP_201_CREATED
        rdata = res.json()

        assert rdata['year'] == data['year']

        assert len(rdata['engagement_list_items']) == len(data['engagement_list_items'])
        hcp1_item = get_item(rdata['engagement_list_items'], 'hcp_id', self.hcp1.id)
        assert hcp1_item['hcp']['id'] == self.hcp1.id
        assert len(rdata['hcp_objectives']) == len(data['hcp_objectives'])

        hcp1_obj = get_item(rdata['hcp_objectives'], 'hcp_id', self.hcp1.id)
        assert hcp1_obj["description"] == "objective of hcp #1"
        assert len(hcp1_obj['deliverables']) == 3

    def test_update_engagement_plan(self):
        # TODO: do it!
        pass
