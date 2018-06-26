from django.utils.text import camel_case_to_spaces
from rest_framework import serializers
from collections import defaultdict, OrderedDict
from .models import (
    EngagementPlan,
    EngagementPlanHCPItem,
    EngagementPlanProjectItem,
    HCP,
    Project,
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


# def fix_nested_id_fields(validated_data):
#     """Used bc DRF sometimes puts *full objects* into _id fields.
#     """
#     r = {}
#     for f, v in validated_data.items():
#         if (
#             f.find('_id') == len(f) - 3 and  # f ends in _id
#             type(v) not in {int, str}
#         ):
#             r[f] = v.id
#         else:
#             r[f] = v
#     return r


class NestedWritableFieldsSerializerMixin:
    class Meta:
        # expect nested_fields : {field_name: WritableSerializerClass}
        # (just use an OrderedDict here if order matters)
        nested_fields = {}

    def create(self, validated_data):
        nested_data = self._extract_nested_data(validated_data)

        # default create
        obj = super().create(validated_data)

        # handle nested objects
        parent_field_name = self._guess_parent_ref_field_name()
        for field_name, nested_items_data in nested_data.items():
            if nested_items_data is None:
                continue
            for item_data in nested_items_data:
                item_data[parent_field_name] = obj.id
                serializer_class = self.Meta.nested_fields[field_name]
                serializer = serializer_class(data=item_data)
                serializer.is_valid()
                serializer.save()

        return obj

    def update(self, obj, validated_data):
        nested_data = self._extract_nested_data(validated_data)

        # default create
        super().update(obj, validated_data)

        # handle nested objects
        parent_field_name = self._guess_parent_ref_field_name()
        for field_name, nested_items_data in nested_data.items():
            if nested_items_data is None:
                continue

            # delete items not present
            getattr(obj, field_name).exclude(
                id__in=(item_data['id']
                        for item_data in nested_items_data
                        if 'id' in item_data)
            ).delete()

            for item_data in nested_items_data:
                serializer_class = self.Meta.nested_fields[field_name]
                model_class = serializer_class.Meta.model
                # update for those with id
                if 'id' in item_data:
                    serializer = serializer_class(
                        model_class.objects.get(id=item_data['id']),
                        item_data,
                        partial=True)
                    serializer.is_valid()
                    serializer.save()
                # crate those without id
                else:
                    item_data[parent_field_name] = obj.id
                    serializer = serializer_class(data=item_data)
                    serializer.is_valid()
                    serializer.save()

    def _extract_nested_data(self, validated_data):
        """Extract nested data first so it doesn't break the regular process
        """
        nested_data = OrderedDict()
        for field_name in self.Meta.nested_fields.keys():
            nested_data[field_name] = validated_data.pop(field_name, None)
        return nested_data

    def _guess_parent_ref_field_name(self):
        """Hacky way to "guess" parent class-referencing field name
        """
        parent_field_name = (
            camel_case_to_spaces(self.Meta.model.__name__).replace(' ', '_') +
            '_id')
        return parent_field_name


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
    user_id = serializers.IntegerField()

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
    # hcp_id = serializers.PrimaryKeyRelatedField(queryset=HCP.objects.all())  # read + write
    # engagement_plan_item_id = serializers.PrimaryKeyRelatedField(
    #     required=False, queryset=EngagementPlanItem.objects.all())  # read + write

    hcp_id = serializers.IntegerField()
    engagement_plan_item_id = serializers.IntegerField()

    deliverables = HCPDeliverableSerializer(many=True)

    class Meta:
        model = HCPObjective
        fields = (
            'id',
            'engagement_plan_item_id',
            'hcp_id',
            'description',
            'approved',
            'approved_at',
            'deliverables',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'deliverables': HCPDeliverableSerializer,
        }

    # def create(self, validated_data):
    #     deliverables = validated_data.pop('deliverables', None)
    #
    #     validated_data = fix_nested_id_fields(validated_data)
    #
    #     # super call to properly handle m2m rels
    #     obj = super().create(validated_data)
    #
    #     # deliverables nested
    #     #########################################
    #     if deliverables is not None:
    #         for deliverable_data in deliverables:
    #             # create directly bc there are no writable nested fields under this
    #             obj.deliverables.create(**deliverable_data)
    #
    #     return obj
    #
    # def update(self, instance, validated_data):
    #     deliverables = validated_data.pop('deliverables', None)
    #     validated_data = fix_nested_id_fields(validated_data)
    #
    #     super().update(instance, validated_data)
    #
    #     # deliverables nested
    #     #########################################
    #     if deliverables is not None:
    #         # delete items not present
    #         instance.deliverables.exclude(
    #             id__in=(deliverable_data['id']
    #                     for deliverable_data in deliverables
    #                     if 'id' in deliverable_data)
    #         ).delete()
    #         for deliverable_data in deliverables:
    #             if 'id' in deliverable_data:  # update existing if with id
    #                 instance.deliverables.filter(id=deliverable_data['id'])\
    #                     .update(**deliverable_data)
    #             else:  # create new if without id
    #                 instance.deliverables.create(**deliverable_data)
    #
    #     return instance


class EngagementPlanHCPItemSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    hcp = HCPSerializer(required=False, read_only=True)

    hcp_objectives = HCPObjectiveSerializer(many=True)

    # hcp_id = serializers.PrimaryKeyRelatedField(queryset=HCP.objects.all())  # read + write
    # engagement_plan_id = serializers.PrimaryKeyRelatedField(
    #     required=False, queryset=EngagementPlan.objects.all())  # read + write

    hcp_id = serializers.IntegerField()
    engagement_plan_id = serializers.IntegerField()

    class Meta:
        model = EngagementPlanHCPItem
        fields = (
            'id',
            'hcp',
            'hcp_id',
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
            'objectives'
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'objectives': HCPObjectiveSerializer,
        }


class EngagementPlanProjectItemItemSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    hcp = HCPSerializer(required=False, read_only=True)
    hcp_id = serializers.IntegerField()
    engagement_plan_id = serializers.IntegerField()
    hcp_objectives = HCPObjectiveSerializer(many=True)

    class Meta:
        model = EngagementPlanProjectItem
        fields = (
            'id',
            'hcp',
            'hcp_id',
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
            'objectives'
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'objectives': HCPObjectiveSerializer,
        }


class EngagementPlanSerializer(serializers.ModelSerializer):
    hcp_items = EngagementPlanHCPItemSerializer(many=True)
    project_items = EngagementPlanProjectItemItemSerializer(many=True)

    class Meta:
        model = EngagementPlan
        fields = (
            'id',
            'user_id',
            'year',
            'approved',
            'approved_at',
            'hcp_items',
            'project_items',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
        nested_fields = {
            'hcp_items': EngagementPlanHCPItemSerializer,
            'project_items': EngagementPlanProjectItemItemSerializer,
        }


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
