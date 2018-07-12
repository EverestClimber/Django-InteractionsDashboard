from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .common import BaseAPITestCase
from interactionscore.models import (
    AffiliateGroup,
    HCP,
    EngagementPlan,
    Interaction,
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
        print_json('test_list_interactions: res', res.json())
        assert res.status_code == status.HTTP_200_OK
        rdata = res.json()

        assert len(rdata) == 1

    def test_create_interaction(self):
        hcp_obj = self.ep1.hcp_items.get(hcp=self.hcp1)\
            .objectives.get(description='hcp 1 obj 1 desc')
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
            'project_id': self.proj1.id,
            'resources': [self.res1.id, self.res2.id],
            'outcome': 'no_further_actions',
            'type_of_interaction': 'face_to_face',
            'time_of_interaction': timezone.now(),
        }
        res = self.client.post(reverse('interaction-list'), data)
        print_json('test_create_interaction: res', res.json())
        assert res.status_code == status.HTTP_201_CREATED

        rdata = res.json()

        assert 'id' in rdata
        assert rdata['user_id'] == self.user_msl1.id
        assert rdata['hcp_id'] == self.hcp1.id
