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


class TestInteractionsAPI(BaseAPITestCase):

    def setUp(self):
        self.client.force_login(self.user_msl1)

    def test_list_interactions(self):
        res = self.client.get(reverse('interaction-list'))
        print_json('res', res.json())
        assert res.status_code == status.HTTP_200_OK
        rdata = res.json()

        assert len(rdata) == 1

    def test_create_interaction(self):
        url = reverse('interaction-list')
        hcp_obj = self.ep1.hcp_objectives.get(hcp=self.hcp1,
                                              description='hcp 1 obj desc')
        data = {
            'hcp_id': self.hcp1.id,
            'description': 'interaction between MSL1 and HCP1',
            'purpose': 'some purpose',
            'is_joint_visit': True,
            'joint_visit_with': 'Mrs Reaper Thanovsky',
            'origin_of_interaction': 'other',
            'origin_of_interaction_other': 'other OI',
            'is_adverse_event': False,
            'hcp_objective_id': hcp_obj.id,
            'projects': self.proj1.id,
            'resources': [self.res1.id, self.res2.id],
            'outcomes': [self.iout1.id, self.iout2.id],
        }
        res = self.client.post(url, data)
        print_json('res', res.json())
        assert res.status_code == status.HTTP_201_CREATED

        rdata = res.json()

        assert 'id' in rdata
        assert rdata['user_id'] == self.user_msl1.id
        assert rdata['hcp_id'] == self.hcp1.id
