from rest_framework import serializers
from collections import defaultdict
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
    InteractionOutcome,
    User,
)


def fix_nested_id_fields(validated_data):
    """Used bc DRF sometimes puts *full objects* into _id fields.
    """
    r = {}
    for f, v in validated_data.items():
        if (
            f.find('_id') == len(f) - 3 and  # f ends in _id
            type(v) not in {int, str}
        ):
            r[f] = v.id
        else:
            r[f] = v
    return r


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


class InteractionOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionOutcome
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
    hcp = HCPSerializer(required=False, read_only=True)
    hcp_id = serializers.PrimaryKeyRelatedField(queryset=HCP.objects.all())  # read + write

    class Meta:
        model = EngagementListItem
        fields = (
            'id',
            'hcp',
            'hcp_id',
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class HCPDeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = HCPDeliverable
        fields = (
            'id',
            'quarter',
            'description',
            'status',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class HCPObjectiveSerializer(serializers.ModelSerializer):
    hcp_id = serializers.PrimaryKeyRelatedField(queryset=HCP.objects.all())  # read + write
    engagement_plan_id = serializers.PrimaryKeyRelatedField(
        required=False, queryset=EngagementPlan.objects.all())  # read + write
    deliverables = HCPDeliverableSerializer(many=True)

    class Meta:
        model = HCPObjective
        fields = (
            'id',
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
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data):
        deliverables = validated_data.pop('deliverables', None)

        validated_data = fix_nested_id_fields(validated_data)

        # super call to properly handle m2m rels
        obj = super().create(validated_data)

        # deliverables nested
        #########################################
        if deliverables is not None:
            for deliverable_data in deliverables:
                # create directly bc there are no writable nested fields under this
                obj.deliverables.create(**deliverable_data)

        return obj

    def update(self, instance, validated_data):
        deliverables = validated_data.pop('deliverables', None)
        validated_data = fix_nested_id_fields(validated_data)

        super().update(instance, validated_data)

        # deliverables nested
        #########################################
        if deliverables is not None:
            # delete items not present
            instance.deliverables.exclude(
                id__in=(deliverable_data['id']
                        for deliverable_data in deliverables
                        if 'id' in deliverable_data)
            ).delete()
            for deliverable_data in deliverables:
                if 'id' in deliverable_data:  # update existing if with id
                    instance.deliverables.filter(id=deliverable_data['id'])\
                        .update(**deliverable_data)
                else:  # create new if without id
                    instance.deliverables.create(**deliverable_data)

        return instance


class EngagementPlanSerializer(serializers.ModelSerializer):
    engagement_list_items = EngagementListItemSerializer(many=True)
    hcp_objectives = HCPObjectiveSerializer(many=True)

    class Meta:
        model = EngagementPlan
        fields = (
            'id',
            'user_id',
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

    def validate(self, data):
        # validate there aren't multiple items referencing same hcp
        engagement_list_items = data.get('engagement_list_items', [])
        items_for_hcp = defaultdict(int)
        for elitem_data in engagement_list_items:
            if 'hcp_id' in elitem_data:
                items_for_hcp[
                    elitem_data['hcp_id']
                    if type(elitem_data['hcp_id']) is str
                    else elitem_data['hcp_id'].id
                ] += 1
        multiple_referenced_hcp_ids = [
            hcp_id for hcp_id, n in items_for_hcp.items()
            if n > 1
        ]
        if multiple_referenced_hcp_ids:
            msg = (
                "Some HCPs are referenced multiple time in engagement_list_items" +
                " which is not allowed. IDs of multiply referenced HCPs: " +
                ", ".join(map(str, multiple_referenced_hcp_ids))
            )
            raise serializers.ValidationError(msg)

        return data

    def create(self, validated_data):
        # set user to current user unless user is admin
        user = self.context['request'].user
        if not user.is_staff and not user.is_superuser:
            validated_data['user'] = user

        engagement_list_items = validated_data.pop('engagement_list_items', None)
        hcp_objectives = validated_data.pop('hcp_objectives', None)

        # call super so it also does right thing for m2m rels
        eplan = super().create(validated_data)

        # engagement_list_items nested
        #########################################
        if engagement_list_items is not None:
            for elitem_data in engagement_list_items:
                # create directly bc there are no writable nested fields under this
                elitem_data = fix_nested_id_fields(elitem_data)
                eplan.engagement_list_items.create(**elitem_data)

        # hcp_objectives nested
        #########################################
        if hcp_objectives is not None:
            for hcp_obj_data in hcp_objectives:
                # use child serializer bc there are deeper level nestings
                hcp_obj_data['engagement_plan_id'] = eplan.id
                hcp_obj_data = fix_nested_id_fields(hcp_obj_data)
                hcp_obj_serializer = HCPObjectiveSerializer(data=hcp_obj_data)
                hcp_obj_serializer.is_valid()
                hcp_obj_serializer.save()

        return eplan

    def update(self, eplan, validated_data):
        engagement_list_items = validated_data.pop('engagement_list_items', None)
        hcp_objectives = validated_data.pop('hcp_objectives', None)

        super().update(eplan, validated_data)

        # engagement_list_items nested
        #########################################
        hcp_ids_for_deleted_items = set()
        if engagement_list_items is not None:
            # delete items not present
            elitems_to_delete = eplan.engagement_list_items.exclude(
                id__in=(elitem_data['id']
                        for elitem_data in engagement_list_items
                        if 'id' in elitem_data)
            )
            hcp_ids_for_deleted_items = set(
                elitem.hcp_id for elitem in elitems_to_delete
            )
            elitems_to_delete.delete()

            for elitem_data in engagement_list_items:
                elitem_data = fix_nested_id_fields(elitem_data)
                if 'id' in elitem_data:  # update existing if with id
                    eplan.engagement_list_items.filter(id=elitem_data['id'])\
                        .update(**elitem_data)
                else:  # create new if without id
                    eplan.engagement_list_items.create(**elitem_data)

        # hcp_objectives nested
        #########################################
        if hcp_objectives is not None:
            # delete objs not present
            eplan.hcp_objectives.exclude(
                id__in=(hcp_obj_data['id']
                        for hcp_obj_data in hcp_objectives
                        if 'id' in hcp_obj_data)
            ).delete()

            # delete objs referenced by deleted elitems
            eplan.hcp_objectives.filter(hcp_id__in=hcp_ids_for_deleted_items).delete()

            for hcp_obj_data in hcp_objectives:
                hcp_obj_data['engagement_plan_id'] = eplan.id
                hcp_obj_data = fix_nested_id_fields(hcp_obj_data)

                if 'id' in hcp_obj_data:  # update existing if with id
                    hcp_obj_serializer = HCPObjectiveSerializer(
                        HCPObjective.objects.get(id=hcp_obj_data['id']),
                        hcp_obj_data,
                        partial=True
                    )
                    hcp_obj_serializer.is_valid()
                    hcp_obj_serializer.save()

                else:  # create new if without id
                    hcp_obj_serializer = HCPObjectiveSerializer(data=hcp_obj_data)
                    hcp_obj_serializer.is_valid()
                    hcp_obj_serializer.save()

        return eplan


class InteractionSerializer(serializers.ModelSerializer):
    hcp = HCPSerializer(required=False)
    hcp_id = serializers.IntegerField()
    hcp_objective = HCPObjectiveSerializer(required=False)
    hcp_objective_id = serializers.IntegerField()
    project = ProjectSerializer(required=False)
    project_id = serializers.IntegerField()

    class Meta:
        model = Interaction
        fields = (
            'id',
            'user_id',
            'hcp',
            'hcp_id',
            'description',
            'purpose',
            'hcp_objective',
            'hcp_objective_id',
            'project',
            'project_id',
            'resources',
            'outcomes',
            'is_joint_visit',
            'joint_visit_with',
            'origin_of_interaction',
            'origin_of_interaction_other',
            'is_adverse_event',
            'appropriate_procedures_followed',
            'is_follow_up_required',
        )

    def create(self, validated_data):
        # set user to current user unless user is admin
        user = self.context['request'].user
        if not user.is_staff and not user.is_superuser:
            validated_data['user'] = user

        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    group_names = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'group_names',
            'permissions',
            'affiliate_groups',
            'tas',
        )

    def get_group_names(self, user):
        return [group.name for group in user.groups.all()]

    def get_permissions(self, user):
        return user.get_all_permissions()
