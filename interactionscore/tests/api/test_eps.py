from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .common import BaseAPITestCase
from interactionscore.models import (
    AffiliateGroup,
    HCP,
    EngagementPlan,
)
from interactionscore.tests.helpers import (
    pp,
    print_json,
    get_item,
    find_item,
)


class TestEngagementPlansAPI(BaseAPITestCase):

    def setUp(self):
        self.client.force_login(self.user_msl1)

    def test_list_engagement_plans(self):
        url = reverse('engagementplan-list')
        res = self.client.get(url)
        print_json('test_list_engagement_plans: res', res.json())
        assert res.status_code == status.HTTP_200_OK
        rdata = res.json()

        assert len(rdata) == 1  # just one bc other belongs to msl2

        # no eps of other msls
        assert sum(ep['user_id'] != self.user_msl1.id for ep in rdata) == 0

    def test_create_engagement_plan(self):
        url = reverse('engagementplan-list')
        data = {
            "year": 2018,
            "hcp_items": [
                {"hcp_id": self.hcp1.id,
                 "objectives": [
                     {"description": "objective of hcp #1", "hcp_id": self.hcp1.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 hcp1 deliverable desc"},
                          {"quarter": 2, "description": "q2 hcp1 deliverable desc"},
                          {"quarter": 3, "description": "q3 hcp1 deliverable desc"},
                      ]}
                 ]},
                {"hcp_id": self.hcp2.id,
                 "objectives": [
                     {"description": "objective 1 of hcp #2", "hcp_id": self.hcp2.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 hcp2 obj1 deliverable desc"},
                          {"quarter": 2, "description": "q2 hcp2 obj1 eliverable desc"},
                      ]},
                     {"description": "objective 2 of hcp #2", "hcp_id": self.hcp2.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 hcp2 obj2 deliverable desc"},
                          {"quarter": 2, "description": "q2 hcp2 obj2 deliverable desc"},
                          {"quarter": 3, "description": "q3 hcp2 obj2 deliverable desc"},
                          {"quarter": 4, "description": "q4 hcp2 obj2 deliverable desc"},
                      ]},
                 ]},
            ],
            "project_items": [
                {"project_id": self.proj1.id,
                 "objectives": [
                     {"description": "objective of proj #1", "project_id": self.proj1.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 proj1 deliverable desc"},
                          {"quarter": 2, "description": "q2 proj1 deliverable desc"},
                          {"quarter": 3, "description": "q3 proj1 deliverable desc"},
                          {"quarter": 4, "description": "q4 proj1 deliverable desc"},
                      ]}
                 ]},
                {"project_id": self.proj2.id,
                 "objectives": [
                     {"description": "objective 1 of proj #2", "project_id": self.proj2.id,
                      "deliverables": [
                          {"quarter": 3, "description": "q3 proj2 obj1 deliverable desc"},
                      ]},
                     {"description": "objective 2 of proj #2", "project_id": self.proj2.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 proj2 obj2 deliverable desc"},
                          {"quarter": 2, "description": "q2 proj2 obj2 deliverable desc"},
                          {"quarter": 3, "description": "q3 proj2 obj2 deliverable desc"},
                      ]},
                 ]},
            ],
        }
        res = self.client.post(url, data)
        print_json('test_create_engagement_plan: res', res.json())
        assert res.status_code == status.HTTP_201_CREATED
        rdata = res.json()

        assert rdata['year'] == data['year']

        ep = EngagementPlan.objects.get(id=rdata['id'])
        assert ep.id == rdata['id']
        assert ep.year == rdata['year']

        assert (len(rdata['hcp_items']) == len(data['hcp_items']) ==
                ep.hcp_items.count())

        rdata_hcp1_item = get_item(rdata['hcp_items'], 'hcp_id', self.hcp1.id)
        assert (len(rdata_hcp1_item['objectives']) == len(data['hcp_items'][0]['objectives']) ==
                ep.hcp_items.get(hcp=self.hcp1).objectives.count())

        rdata_hcp2_item = get_item(rdata['hcp_items'], 'hcp_id', self.hcp2.id)
        assert (len(rdata_hcp2_item['objectives']) == len(data['hcp_items'][1]['objectives']) ==
                ep.hcp_items.get(hcp=self.hcp2).objectives.count())

        assert (len(rdata_hcp1_item['objectives'][0]['deliverables']) ==
                len(data['hcp_items'][0]['objectives'][0]['deliverables']) ==
                ep.hcp_items.get(hcp=self.hcp1).objectives.first().deliverables.count())

        rdata_hcp2_item_obj1 = get_item(rdata_hcp2_item['objectives'], 'description', "objective 1 of hcp #2")
        assert (len(rdata_hcp2_item_obj1['deliverables']) ==
                len(data['hcp_items'][1]['objectives'][0]['deliverables']) ==
                ep.hcp_items.get(hcp=self.hcp2).objectives.get(
                    description="objective 1 of hcp #2"
                ).deliverables.count())

        rdata_hcp2_item_obj2 = get_item(rdata_hcp2_item['objectives'], 'description', "objective 2 of hcp #2")
        assert (len(rdata_hcp2_item_obj2['deliverables']) ==
                len(data['hcp_items'][1]['objectives'][1]['deliverables']) ==
                ep.hcp_items.get(hcp=self.hcp2).objectives.get(
                    description="objective 2 of hcp #2"
                ).deliverables.count())

        assert (len(rdata['project_items']) == len(data['project_items']) ==
                ep.project_items.count())

        rdata_proj1_item = get_item(rdata['project_items'], 'project_id', self.proj1.id)
        assert (len(rdata_proj1_item['objectives']) == len(data['project_items'][0]['objectives']) ==
                ep.project_items.get(project=self.proj1).objectives.count())

        rdata_proj2_item = get_item(rdata['project_items'], 'project_id', self.proj2.id)
        assert (len(rdata_proj2_item['objectives']) == len(data['project_items'][1]['objectives']) ==
                ep.project_items.get(project=self.proj2).objectives.count())

        assert (len(rdata_proj1_item['objectives'][0]['deliverables']) ==
                len(data['project_items'][0]['objectives'][0]['deliverables']) ==
                ep.project_items.get(project=self.proj1).objectives.first().deliverables.count())

        rdata_proj2_item_obj1 = get_item(rdata_proj2_item['objectives'], 'description', "objective 1 of proj #2")
        assert (len(rdata_proj2_item_obj1['deliverables']) ==
                len(data['project_items'][1]['objectives'][0]['deliverables']) ==
                ep.project_items.get(project=self.proj2).objectives.get(
                    description="objective 1 of proj #2"
                ).deliverables.count())

        rdata_proj2_item_obj2 = get_item(rdata_proj2_item['objectives'], 'description', "objective 2 of proj #2")
        assert (len(rdata_proj2_item_obj2['deliverables']) ==
                len(data['project_items'][1]['objectives'][1]['deliverables']) ==
                ep.project_items.get(project=self.proj2).objectives.get(
                    description="objective 2 of proj #2"
                ).deliverables.count())

    def test_update_engagement_plan(self):
        ep_before_update = self.ep1
        data = {
            "year": 2019,
            "hcp_items": [
                # update hcp1 item
                {"id": self.ep1.hcp_items.get(hcp=self.hcp1).id,
                 "objectives": [
                     # update deliverable of existing item
                     {"id": self.ep1.hcp_items.get(hcp=self.hcp1).objectives.first().id,
                      "deliverables": [
                          # delete q1
                          # update q2
                          {"id": self.ep1.hcp_items.get(hcp=self.hcp1).objectives.first()
                              .deliverables.get(quarter=2).id,
                           "description": "updated q2 hcp1 deliverable desc"},
                          # leave q3 unchanged
                          {"id": self.ep1.hcp_items.get(hcp=self.hcp1).objectives.first()
                              .deliverables.get(quarter=3).id}
                      ]}
                 ]},
                # ...delete hcp2 (by not passing it here!)
                # create new item for hcp3
                {"hcp_id": self.hcp3.id,
                 "objectives": [
                     {"description": "objective 1 of hcp #3", "hcp_id": self.hcp3.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 hcp3 obj1 deliverable desc"},
                          {"quarter": 2, "description": "q2 hcp3 obj1 eliverable desc"},
                      ]},
                     {"description": "objective 2 of hcp #3", "hcp_id": self.hcp3.id,
                      "deliverables": [
                          {"quarter": 1, "description": "q1 hcp3 obj2 deliverable desc"},
                          {"quarter": 2, "description": "q2 hcp3 obj2 deliverable desc"},
                          {"quarter": 3, "description": "q3 hcp3 obj2 deliverable desc"},
                          {"quarter": 4, "description": "q4 hcp3 obj2 deliverable desc"},
                      ]},
                 ]},
            ],
            "project_items": [
                # leave proj1 unchanged
                {"id": self.ep1.project_items.get(project=self.proj1).id},
                # leave proj2 unchanged
                {"id": self.ep1.project_items.get(project=self.proj2).id},
            ],
        }
        res = self.client.patch(
            reverse('engagementplan-detail', args=[self.ep1.id]),
            data)
        print_json('test_update_engagement_plan: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        assert rdata['id'] == self.ep1.id

        # get post-update EP
        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert ep_before_update.updated_at < ep.updated_at

        assert (ep.hcp_items.count() == len(data['hcp_items']) ==
                len(rdata['hcp_items']))
        assert ep.hcp_items.filter(hcp=self.hcp1).count() == 1
        assert ep.hcp_items.filter(hcp=self.hcp2).exists() is False
        assert ep.hcp_items.filter(hcp=self.hcp3).count() == 1

        assert (ep.hcp_items.get(hcp=self.hcp1).objectives.count() ==
                len(data['hcp_items'][0]['objectives']))
        assert (ep.hcp_items.get(hcp=self.hcp1).objectives.first().deliverables.count() ==
                len(data['hcp_items'][0]['objectives'][0]['deliverables']))
        assert not ep.hcp_items.get(hcp=self.hcp1).objectives.first()\
            .deliverables.filter(quarter=1).exists()
        assert (
            ep.hcp_items.get(hcp=self.hcp1).objectives.first().deliverables.get(quarter=2).description ==
            "updated q2 hcp1 deliverable desc")
        assert ep.hcp_items.get(hcp=self.hcp1).objectives.first()\
            .deliverables.filter(quarter=3).exists()

        assert (ep.hcp_items.get(hcp=self.hcp3).objectives.count() ==
                len(get_item(rdata['hcp_items'], 'hcp_id', self.hcp3.id)['objectives']) ==
                len(data['hcp_items'][1]['objectives']))

        assert (ep.project_items.count() == len(data['project_items']) ==
                len(rdata['project_items']))

    def test_approve_ep_all_hcp_items(self):
        # required for the test to make sense:
        assert self.ep1.approved is False

        self.client.force_login(self.user_man1)
        res = self.client.post(
            reverse('engagementplan-approve', args=[self.ep1.id]),
            {
                'hcp_items': True,
            })
        print_json('test_approve_ep_all_hcp_items: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert rdata['id'] == self.ep1.id

        assert rdata['approved'] is ep.approved is True
        assert rdata['approved_at'] is not None
        assert not ep.hcp_items.filter(approved=False).exists()

    def test_approve_ep_some_hcp_items(self):
        # required for the test to make sense:
        assert self.ep1.approved is False

        self.client.force_login(self.user_man1)
        res = self.client.post(
            reverse('engagementplan-approve', args=[self.ep1.id]),
            {
                'hcp_items_ids': [self.ep1.hcp_items.get(hcp=self.hcp1).id],
            })
        print_json('test_approve_ep_some_hcp_items: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert rdata['id'] == self.ep1.id

        assert rdata['approved'] is ep.approved is False
        assert rdata['approved_at'] is None
        assert ep.hcp_items.get(hcp=self.hcp1).approved is True
        assert ep.hcp_items.get(hcp=self.hcp2).approved is False

    def test_approve_ep_all_hcp_items_by_id(self):
        # required for the test to make sense:
        assert self.ep1.approved is False

        self.client.force_login(self.user_man1)
        res = self.client.post(
            reverse('engagementplan-approve', args=[self.ep1.id]),
            {
                'hcp_items_ids': [it.id for it in self.ep1.hcp_items.all()],
            })
        print_json('test_approve_ep_all_hcp_items_by_id: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert rdata['id'] == self.ep1.id

        assert rdata['approved'] is ep.approved is True
        assert rdata['approved_at'] is not None
        assert not ep.hcp_items.filter(approved=False).exists()

    def test_unapprove_ep_all_hcp_items(self):
        # required for the test to make sense:
        assert self.ep1.approved is False

        self.ep1.hcp_items.get(hcp=self.hcp1).approve()

        self.client.force_login(self.user_man1)
        res = self.client.post(
            reverse('engagementplan-unapprove', args=[self.ep1.id]),
            {
                'hcp_items': True,
            })
        print_json('test_approve_ep_all_hcp_items: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert rdata['id'] == self.ep1.id

        assert rdata['approved'] is ep.approved is False
        assert not ep.hcp_items.filter(approved=True).exists()

    def test_unapprove_ep_some_hcp_items(self):
        # required for the test to make sense:
        assert self.ep1.approved is False

        for it in self.ep1.hcp_items.all():
            it.approve()

        self.client.force_login(self.user_man1)
        res = self.client.post(
            reverse('engagementplan-unapprove', args=[self.ep1.id]),
            {
                'hcp_items_ids': [self.ep1.hcp_items.get(hcp=self.hcp1).id],
            })
        print_json('test_approve_ep_some_hcp_items: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert rdata['id'] == self.ep1.id

        assert rdata['approved'] is ep.approved is False
        assert ep.hcp_items.get(hcp=self.hcp1).approved is False
        assert ep.hcp_items.get(hcp=self.hcp2).approved is True

    def test_unapprove_ep_all_hcp_items_by_id(self):
        self.ep1.approve()
        for it in self.ep1.hcp_items.all():
            it.approve()

        self.client.force_login(self.user_man1)
        res = self.client.post(
            reverse('engagementplan-unapprove', args=[self.ep1.id]),
            {
                'hcp_items_ids': [it.id for it in self.ep1.hcp_items.all()],
            })
        print_json('test_approve_ep_all_hcp_items_by_id: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        ep = EngagementPlan.objects.get(id=self.ep1.id)

        assert rdata['id'] == self.ep1.id

        assert rdata['approved'] is ep.approved is False
        assert not ep.hcp_items.filter(approved=True).exists()

        # TODO: prover way to revert each test to original state
        self.ep1.unapprove()

