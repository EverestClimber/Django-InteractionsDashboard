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
            'year',
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
