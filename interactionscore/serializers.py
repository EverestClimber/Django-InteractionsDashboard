from rest_framework import serializers
from .models import (
    EngagementPlan,
)


class EngagementPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementPlan
        fields = (
            'id',
            'user',
            'approved',
        )
        read_only_fields = ('approved',)
