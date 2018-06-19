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

    def create(self, validated_data):
        user = self.context['request'].user

        # set user to current user unless an admin user sets it explicitly
        if (
            'user' not in validated_data or
            (not user.is_staff and not user.is_superuser)
        ):
            validated_data['user'] = user

        eplan = EngagementPlan.objects.create(**validated_data)
        return eplan
