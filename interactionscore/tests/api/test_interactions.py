from django.urls import reverse
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
        hcp_obj = self.ep1.items.get(hcp=self.hcp1)\
            .hcp_objectives.get(description='hcp 1 obj desc')
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
            'outcomes': [self.iout1.id, self.iout2.id],
        }
        res = self.client.post(reverse('interaction-list'), data)
        print_json('test_create_interaction: res', res.json())
        assert res.status_code == status.HTTP_201_CREATED

        rdata = res.json()

        assert 'id' in rdata
        assert rdata['user_id'] == self.user_msl1.id
        assert rdata['hcp_id'] == self.hcp1.id

    def test_update_interactions(self):
        interaction_before_update = self.inter1
        data = {
            'description': 'updated interaction between MSL1 and HCP1',
            'is_joint_visit': True,
            'hcp_id': self.hcp2.id,
            'resources': [self.res3.id, self.res2.id],
            'outcomes': [self.iout3.id, self.iout2.id],
        }
        res = self.client.patch(
            reverse('interaction-detail', args=[self.inter1.id]),
            data)
        print_json('test_update_interactions: res', res.json())
        assert res.status_code // 100 == 2

        rdata = res.json()

        assert rdata['id'] == self.inter1.id

        interaction_after_update = Interaction.objects.get(id=self.inter1.id)

        assert interaction_before_update.description != rdata['description']

        assert (rdata['description'] == data['description'] ==
                interaction_after_update.description)

        assert (rdata['is_joint_visit'] == data['is_joint_visit'] ==
                interaction_after_update.is_joint_visit)

        assert rdata['hcp_id'] == data['hcp_id'] == interaction_after_update.hcp_id

        assert rdata['hcp']['id'] == data['hcp_id'] == interaction_after_update.hcp.id

        assert (set(rdata['resources']) == set(rdata['resources']) ==
                set(r.id for r in interaction_after_update.resources.all()))

        assert (set(rdata['outcomes']) == set(rdata['outcomes']) ==
                set(o.id for o in interaction_after_update.outcomes.all()))
