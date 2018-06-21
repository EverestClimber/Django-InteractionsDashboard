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
        print_json('test_create_engagement_plan: res', res.json())
        assert res.status_code == status.HTTP_201_CREATED
        rdata = res.json()

        assert rdata['year'] == data['year']

        ep = EngagementPlan.objects.get(id=rdata['id'])
        assert ep.id == rdata['id']
        assert str(ep.year) == rdata['year']

        assert len(rdata['engagement_list_items']) == len(data['engagement_list_items'])
        assert ep.engagement_list_items.count() == len(data['engagement_list_items'])

        hcp1_item = get_item(rdata['engagement_list_items'], 'hcp_id', self.hcp1.id)
        assert hcp1_item['hcp']['id'] == self.hcp1.id

        assert len(rdata['hcp_objectives']) == len(data['hcp_objectives'])
        assert ep.hcp_objectives.count() == len(data['hcp_objectives'])

        hcp1_obj = get_item(rdata['hcp_objectives'], 'hcp_id', self.hcp1.id)
        assert hcp1_obj["description"] == "objective of hcp #1"
        assert len(hcp1_obj['deliverables']) == 3

    def test_update_engagement_plan(self):
        ep_before_update = self.ep1
        data = {
            "year": "2018-01-01",
            "engagement_list_items": [
                # leave hcp1 item unchanged
                {"id": self.ep1.engagement_list_items.get(hcp=self.hcp1).id},
                # ...delete hcp2 (by not passing it here!)
                # create new item for hcp3
                {"hcp_id": self.hcp3.id},
            ],
            "hcp_objectives": [
                {  # update obj 1 for hcp1
                    "id": self.ep1.hcp_objectives.get(hcp=self.hcp1,
                                                      description='hcp 1 obj desc').id,
                    "description": "updated description",
                    "deliverables": [
                        # delete q1 deliverable by omitting it
                        {  # leave q2 deliverable unchanged
                            "id": self.ep1.hcp_objectives.get(
                                hcp=self.hcp1, description='hcp 1 obj desc'
                            ).deliverables.get(quarter=2).id,
                        },
                        {  # update q3 deliverable
                            "id": self.ep1.hcp_objectives.get(
                                hcp=self.hcp1, description='hcp 1 obj desc'
                            ).deliverables.get(quarter=3).id,
                            "description": "q3 desc updated"
                        }
                    ]
                },
                # ...second obj of hcp1 gets deleted (bc it's not present here!)
                # ...obj for hcp2 gets deleted bc hcp2 item was deleted
                {  # add obj for hcp3
                    "hcp_id": self.hcp3.id,
                    "description": "hcp3 obj desc",
                    "deliverables": [
                        {"quarter": 3, "description": "desc for q3"}
                    ]
                }
            ]
        }
        res = self.client.patch(
            reverse('engagementplan-detail', args=[self.ep1.id]),
            data)
        print_json('test_update_engagement_plan: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        assert rdata['id'] == self.ep1.id

        ep_after_update = EngagementPlan.objects.get(id=self.ep1.id)

        assert ep_before_update.updated_at < ep_after_update.updated_at

        # engagement list items
        assert (len(rdata['engagement_list_items']) ==
                ep_after_update.engagement_list_items.count() ==
                len(data['engagement_list_items']))

        assert (  # hcp1 item maintains id
            get_item(rdata['engagement_list_items'], 'hcp_id', self.hcp1.id)['id'] ==
            ep_after_update.engagement_list_items.get(hcp=self.hcp1).id
        )

        assert find_item(rdata['engagement_list_items'], 'hcp_id', self.hcp2.id) is None

        hcp3_item = find_item(rdata['engagement_list_items'], 'hcp_id', self.hcp3.id)
        assert hcp3_item is not None
        assert hcp3_item['hcp']['id'] == self.hcp3.id

        # hcp objectives
        assert (len(rdata['hcp_objectives']) ==
                ep_after_update.hcp_objectives.count() ==
                len(data['hcp_objectives']))

        returned_hcp1_obj = get_item(rdata['hcp_objectives'], 'hcp_id', self.hcp1.id)
        assert (  # first obj for hcp1 item maintains id (and there is only 1 obj for hcp1 now)
            returned_hcp1_obj['id'] ==
            ep_after_update.hcp_objectives.get(hcp=self.hcp1).id ==
            data['hcp_objectives'][0]['id']
        )
        assert (
            len(returned_hcp1_obj['deliverables']) ==
            ep_after_update.hcp_objectives.get(hcp=self.hcp1).deliverables.count() ==
            len(data['hcp_objectives'][0]['deliverables'])
        )
        assert (
            get_item(returned_hcp1_obj['deliverables'], 'quarter', 3)['description'] ==
            ep_after_update.hcp_objectives.get(hcp=self.hcp1).deliverables.get(quarter=3).description ==
            data['hcp_objectives'][0]['deliverables'][1]['description']
        )
