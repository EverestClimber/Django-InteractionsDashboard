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
)


class TestEngagementPlansAPI(BaseAPITestCase):

    def setUp(self):
        self.client.force_login(self.user_msl1)

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
        # TODO: do it!
        pass
