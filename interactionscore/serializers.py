from rest_framework import serializers
from .models import (
    EngagementPlan,
    EngagementListItem,
    HCP,
    HCPObjective,
    HCPDeliverable,
    AffiliateGroup,
    TherapeuticArea,
    Resource,
    Project,
    Interaction,
)


class AffiliateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateGroup
        fields = ('id', 'name')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name')


class TherapeuticAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapeuticArea
        fields = ('id', 'name')


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('id', 'user_id', 'url', 'file')


class HCPSerializer(serializers.ModelSerializer):
    class Meta:
        model = HCP
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'institution_name',
            'institution_address',
            'contact_preference',
            'affiliate_groups',
            'tas',
        )


class EngagementListItemSerializer(serializers.ModelSerializer):
    hcp = HCPSerializer(required=False)  # read only!
    hcp_id = serializers.PrimaryKeyRelatedField(queryset=HCP.objects.all())  # read + write

    class Meta:
        model = EngagementListItem
        fields = (
            'hcp',
            'hcp_id',
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )


class HCPDeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = HCPDeliverable
        fields = (
            'quarter',
            'description',
            'status',
        )


class HCPObjectiveSerializer(serializers.ModelSerializer):
    hcp_id = serializers.PrimaryKeyRelatedField(queryset=HCP.objects.all())  # read + write
    engagement_plan_id = serializers.PrimaryKeyRelatedField(
        required=False, queryset=EngagementPlan.objects.all())  # read + write
    deliverables = HCPDeliverableSerializer(many=True)

    class Meta:
        model = HCPObjective
        fields = (
            'engagement_plan_id',
            'hcp_id',
            'description',
            'approved',
            'approved_at',
            'deliverables',
            # 'comments',
            'created_at',
            'updated_at',
        )

    def create(self, validated_data):
        deliverables = validated_data.pop('deliverables', [])

        # unfuck DRF handling of write to _id fields
        validated_data['engagement_plan'] = validated_data.pop('engagement_plan_id')
        validated_data['hcp'] = validated_data.pop('hcp_id')

        # super call to properly handle m2m rels
        obj = super().create(validated_data)

        for deliverable_data in deliverables:
            # create directly bc there are no writable nested fields under this
            obj.deliverables.create(**deliverable_data)

        return obj


class EngagementPlanSerializer(serializers.ModelSerializer):
    engagement_list_items = EngagementListItemSerializer(many=True)
    hcp_objectives = HCPObjectiveSerializer(many=True)

    class Meta:
        model = EngagementPlan
        fields = (
            'id',
            'user',
            'year',
            'approved',
            'approved_at',
            'engagement_list_items',
            'hcp_objectives',
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

        engagement_list_items = validated_data.pop('engagement_list_items', [])
        hcp_objectives = validated_data.pop('hcp_objectives', [])

        # call super so it also does right thing for m2m rels
        eplan = super().create(validated_data)

        for elitem_data in engagement_list_items:
            # create directly bc there are no writable nested fields under this
            eplan.engagement_list_items.create(hcp=elitem_data.pop('hcp_id'),
                                               **elitem_data)

        for hcp_obj_data in hcp_objectives:
            # use child serializer bc there are deeper level nestings

            # unfuck DRF handling of write to _id fields
            hcp_obj_data['engagement_plan_id'] = eplan.id
            hcp_obj_data['hcp_id'] = hcp_obj_data.pop('hcp_id').id

            hcp_obj_serializer = HCPObjectiveSerializer(data=hcp_obj_data)
            hcp_obj_serializer.is_valid()
            hcp_obj_serializer.save()

        return eplan

    # def update(self, instance, validated_data):
    #     pass


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = (
            'id',
            'user',
        )
