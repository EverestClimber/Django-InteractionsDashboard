from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status, mixins
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
)

from .models import (
    EngagementPlan,
    EngagementPlanPerms,
    InteractionPerms,
    HCP,
    AffiliateGroup,
    TherapeuticArea,
    Resource,
    Project,
    Interaction,
    HCPObjective,
    User,
    BrandCriticalSuccessFactor,
    MedicalPlanObjective,
)
from .serializers import (
    AffiliateGroupSerializer,
    ProjectSerializer,
    TherapeuticAreaSerializer,
    ResourceSerializer,
    EngagementPlanSerializer,
    HCPSerializer,
    InteractionSerializer,
    UserSerializer,
    HCPObjectiveSerializer,
    BrandCriticalSuccessFactorSerializer,
    MedicalPlanObjectiveSerializer,
)


class AffiliateGroupViewSet(viewsets.ModelViewSet):
    queryset = AffiliateGroup.objects.all()
    serializer_class = AffiliateGroupSerializer
    permission_classes = (IsAuthenticated,)


class BrandCriticalSuccessFactorViewSet(viewsets.ModelViewSet):
    queryset = BrandCriticalSuccessFactor.objects.all()
    serializer_class = BrandCriticalSuccessFactorSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)

        user_id = self.request.query_params.get('user', None)
        ta_ids = self.request.query_params.get('tas', None)
        if ta_ids:
            ta_ids = ta_ids.split(',')
        affiliate_group_ids = self.request.query_params.get('affiliate_groups', None)
        if affiliate_group_ids:
            affiliate_group_ids = affiliate_group_ids.split(',')

        if user_id:
            qs = qs.filter(user_id=user_id)

        if not ta_ids and not self.request.user.is_staff:
            ta_ids = self.request.user.tas.all()
        if ta_ids:
            qs = qs.filter(tas__in=ta_ids)

        if not affiliate_group_ids and not self.request.user.is_staff:
            affiliate_group_ids = self.request.user.affiliate_groups.all()
        if affiliate_group_ids:
            qs = qs.filter(affiliate_groups__in=affiliate_group_ids)

        return qs.distinct()


class MedicalPlanObjectiveSerializerViewSet(viewsets.ModelViewSet):
    queryset = MedicalPlanObjective.objects.all()
    serializer_class = MedicalPlanObjectiveSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)

        user_id = self.request.query_params.get('user', None)
        ta_ids = self.request.query_params.get('tas', None)
        if ta_ids:
            ta_ids = ta_ids.split(',')
        affiliate_group_ids = self.request.query_params.get('affiliate_groups', None)
        if affiliate_group_ids:
            affiliate_group_ids = affiliate_group_ids.split(',')

        if user_id:
            qs = qs.filter(user_id=user_id)

        if not ta_ids and not self.request.user.is_staff:
            ta_ids = self.request.user.tas.all()
        if ta_ids:
            qs = qs.filter(tas__in=ta_ids)

        if not affiliate_group_ids and not self.request.user.is_staff:
            affiliate_group_ids = self.request.user.affiliate_groups.all()
        if affiliate_group_ids:
            qs = qs.filter(affiliate_groups__in=affiliate_group_ids)

        return qs.distinct()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    list:
    ### **URL Query Parameters**

    * `user=<id>` - list Projects belonging to user
    * `type=...` - filter Projects by type
    * `tas=<id1>,<id2>,...` - get Projects for TA(s)
    * `affiliate_groups=<id1>,<id2>,...` - get Projects for AffiliateGroup(s)
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)

        user_id = self.request.query_params.get('user', None)
        project_type = self.request.query_params.get('type', None)
        ta_ids = self.request.query_params.get('tas', None)
        if ta_ids:
            ta_ids = ta_ids.split(',')
        affiliate_group_ids = self.request.query_params.get('affiliate_groups', None)
        if affiliate_group_ids:
            affiliate_group_ids = affiliate_group_ids.split(',')

        if user_id:
            qs = qs.filter(user_id=user_id)

        if project_type:
            qs = qs.filter(type=project_type)

        if not ta_ids and not self.request.user.is_staff:
            ta_ids = self.request.user.tas.all()
        if ta_ids:
            qs = qs.filter(tas__in=ta_ids)

        if not affiliate_group_ids and not self.request.user.is_staff:
            affiliate_group_ids = self.request.user.affiliate_groups.all()
        if affiliate_group_ids:
            qs = qs.filter(affiliate_groups__in=affiliate_group_ids)

        return qs.distinct()


class TherapeuticAreaViewSet(viewsets.ModelViewSet):
    queryset = TherapeuticArea.objects.all()
    serializer_class = TherapeuticAreaSerializer
    permission_classes = (IsAuthenticated,)


class ResourceViewSet(viewsets.ModelViewSet):
    """
    list:
    ### **URL Query Parameters**

    * `tas=<id1>,<id2>,...` - get Resources for TA(s)
    * `affiliate_groups=<id1>,<id2>,...` - get Resources for AffiliateGroup(s)
    * `user=<id>` - get Resources with TAs or AGs in common with user
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)

        user_id = self.request.query_params.get('user', None)
        ta_ids = self.request.query_params.get('tas', None)
        if ta_ids:
            ta_ids = ta_ids.split(',')
        affiliate_group_ids = self.request.query_params.get('affiliate_groups', None)
        if affiliate_group_ids:
            affiliate_group_ids = affiliate_group_ids.split(',')

        if user_id:
            user = User.objects.get(id=user_id)
            qs = qs.filter(
                Q(tas__in=user.tas.all()) |
                Q(affiliate_groups__in=user.affiliate_groups.all())
            )

        if not ta_ids and not self.request.user.is_staff:
            ta_ids = self.request.user.tas.all()
        if ta_ids:
            qs = qs.filter(tas__in=ta_ids)

        if not affiliate_group_ids and not self.request.user.is_staff:
            affiliate_group_ids = self.request.user.affiliate_groups.all()
        if affiliate_group_ids:
            qs = qs.filter(affiliate_groups__in=affiliate_group_ids)

        return qs.distinct()


class HCPViewSet(viewsets.ModelViewSet):
    """
    list:
    ### **URL Query Parameters**

    * `user=<id>` - get HCPs with TAs or AGs in common with user
    * `user=<id>` & `engagement_plan=current` - get HCPs referenced in this user's current EP
    * `engagement_plan=<id>` - get HCPs referenced in this EP
    """

    queryset = HCP.objects.all()
    serializer_class = HCPSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)

        #################################################
        # Filtering
        #################################################

        user_id = self.request.query_params.get('user', None)
        engagement_plan = self.request.query_params.get('engagement_plan', None)

        engagement_plan_id = None
        if engagement_plan:
            if engagement_plan == 'current':
                if not user_id:
                    raise APIException('user needs to be specified '
                                       'when requesting current EngagementPlan')
                engagement_plan_id = EngagementPlan.objects.get(
                    user_id=user_id,
                    year=timezone.now().year
                ).id
            else:
                engagement_plan_id = engagement_plan

        # get HCPs in user's current engagement plan
        # (or, in general, get HCPs referenced by an EP while also asserting EP
        #  belongs to a user)
        if user_id and engagement_plan_id:
            qs = qs.filter(
                engagementplanhcpitem__engagement_plan_id=engagement_plan_id,
                engagementplanhcpitem__engagement_plan__user_id=user_id,
            )
        # get HCPs with TAs and AGs in common with this user
        elif user_id:
            user = User.objects.get(id=user_id)
            qs = qs.filter(
                Q(tas__in=user.tas.all()) |
                Q(affiliate_groups__in=user.affiliate_groups.all())
            )
        # get HCPs reference in this EP
        elif engagement_plan_id:
            qs = qs.filter(engagementplanhcpitem__engagement_plan_id=engagement_plan_id)

        if not self.request.user.is_staff:
            qs = qs.filter(
                affiliate_groups__in=self.request.user.affiliate_groups.all(),
                tas__in=self.request.user.tas.all(),
            )

        #################################################
        # Searching
        #################################################

        search = self.request.query_params.get('search', None)
        if search:
            qs = HCP.add_full_text_search_to_query(qs, search)

        return qs.distinct()


class HCPObjectiveViewSet(viewsets.ModelViewSet):
    """
    list:
    ### **URL Query Parameters**

    * `user=<id>` (& `engagement_plan=current` also assumed by default) -
      get HCPObjectives referenced in this user's current EP
    * `engagement_plan=<id>` - get HCPObjectives referenced in this EP
    """

    queryset = HCPObjective.objects.all()
    serializer_class = HCPObjectiveSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)

        user_id = self.request.query_params.get('user', None)
        hcp_id = self.request.query_params.get('hcp', None)
        engagement_plan = self.request.query_params.get('engagement_plan', None)

        if user_id and not engagement_plan:
            engagement_plan = 'current'

        engagement_plan_id = None
        if engagement_plan:
            if engagement_plan == 'current' and user_id:
                eplan = EngagementPlan.objects.filter(
                    user_id=user_id,
                    year=timezone.now().year
                ).first()
                if not eplan:
                    return qs.none()
                engagement_plan_id = eplan.id
            else:
                engagement_plan_id = engagement_plan

        if hcp_id:
            qs = qs.filter(hcp_id=hcp_id)
            if not user_id and engagement_plan == 'current':
                qs = qs.filter(
                    engagement_plan_item__engagement_plan___year=timezone.now().year,
                )

        # get HCPObjs in user's current engagement plan
        # (or, in general, get HCPObjs referenced by an EP while also asserting
        #  EP belongs to a user)
        if user_id and engagement_plan_id:
            qs = qs.filter(
                engagement_plan_item__approved=True,
                engagement_plan_item__engagement_plan_id=engagement_plan_id,
                engagement_plan_item__engagement_plan__user_id=user_id,
            )
        # get HCPObjs reference in this EP
        elif engagement_plan_id:
            qs = qs.filter(
                engagement_plan_item__approved=True,
                engagement_plan_item__engagement_plan_id=engagement_plan_id)

        return qs.distinct()


class InteractionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = (IsAuthenticated,)

    #################################################
    # Permissions
    #################################################

    def get_queryset(self):
        qs = super().get_queryset()
        # staff users and those with list_all_ep perm can see all
        if (
            self.request.user.is_staff or
            self.request.user.has_interactions_perm(InteractionPerms.list_all_interaction)
        ):
            return qs
        # list_own_ag_interaction perm allows listing items from same AG as user
        if self.request.user.has_interactions_perm(InteractionPerms.list_own_ag_interaction):
            return qs.filter(user__affiliate_groups__in=self.request.user.affiliate_groups.all())
        # by default a user only has access to his own Interactions
        return qs.filter(user=self.request.user)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)

        user = self.request.user

        if self.action == 'create':
            if user.has_interactions_perm('add_engagementplan'):
                return  # allow

        if self.action in {'list', 'retrieve'}:  # restricted by get_queryset above
            return  # allow


class EngagementPlanViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = EngagementPlan.objects.all()
    serializer_class = EngagementPlanSerializer
    permission_classes = (IsAuthenticated,)

    #################################################
    # Permissions
    #################################################

    def get_queryset(self):
        qs = super().get_queryset()
        # staff users and those with list_all_ep perm can see all
        if (
            self.request.user.is_staff or
            self.request.user.has_interactions_perm(EngagementPlanPerms.list_all_ep)
        ):
            return qs
        # list_own_ag_ep perm allows listing EPs from same AG as user
        if self.request.user.has_interactions_perm(EngagementPlanPerms.list_own_ag_ep):
            return qs.filter(user__affiliate_groups__in=self.request.user.affiliate_groups.all())
        # by default a user only has access to his own EPs
        return qs.filter(user=self.request.user)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)

        user = self.request.user

        if self.action == 'create':
            if user.has_interactions_perm('add_engagementplan'):
                return  # allow

        if self.action in {'list', 'retrieve'}:  # restricted by get_queryset above
            return  # allow

        if self.action in {'approve', 'unapprove'}:
            # users with approve_all_ep perm can approve all EPs
            if user.has_interactions_perm(EngagementPlanPerms.approve_all_ep):
                return  # allow
            # users with approve_own_ag_ep can only approve EPs within same Affiliate Group
            if user.has_interactions_perm(EngagementPlanPerms.approve_own_ag_ep):
                if (obj.user.affiliate_groups.all() & user.affiliate_groups.all()).exists():
                    return  # allow
            # by default deny (raises exc)
            self.permission_denied(request, 'User does not have required permission')

        if self.action in {'destroy', 'update', 'partial_update'}:
            if user.has_interactions_perm('change_engagementplan'):
                return  # allow
            if user.has_interactions_perm(EngagementPlanPerms.change_own_current_ep):
                if not user or obj.user != user:
                    self.permission_denied(request, "User does not own engagement plan")
                if obj.year != timezone.now().year:
                    self.permission_denied(request, "Only current (year) engagement plan can be changed")
                return  # if no condition failed, allow

    #################################################
    # Filtering
    #################################################

    def filter_queryset(self, qs):
        qs = super().filter_queryset(qs)
        approved = self.request.query_params.get('approved', None)
        if approved is not None:
            if approved == 'true':
                approved = True
            elif approved == 'false':
                approved = False
            else:
                raise APIException("Parameter 'approved' only have values 'true' or 'false'",
                                   code=status.HTTP_400_BAD_REQUEST)  # TODO: fix to really return http 400
            return qs.filter(approved=approved)
        return qs

    #################################################
    # Actions
    #################################################

    @action(methods=['post'], detail=True, url_path='approve')
    def approve(self, request, pk=None):
        """
        ### **Body Parameters**
        When no params are provided entire EP gets approved.
        When providing params, give one of these:

        * `hcp_items : Bool`
        * `hcp_items_ids : Bool`

        *Ignore body params table that maybe below this action, none of those are used.*

        ---
        """
        eplan = self.get_object()

        hcp_items = request.data.get('hcp_items')
        hcp_items_ids = request.data.get('hcp_items_ids')

        if hcp_items:
            for hcp_item in eplan.hcp_items.all():
                hcp_item.approve()
            eplan.approve()

        if hcp_items_ids:
            for hcp_item in hcp_items_ids:
                eplan.hcp_items.get(id=hcp_item).approve()
            if not eplan.hcp_items.filter(approved=False).exists():
                eplan.approve()

        return Response(self.get_serializer(eplan).data)

    @action(methods=['post'], detail=True, url_path='unapprove')
    def unapprove(self, request, pk=None):
        """
        ### **Body Parameters**
        When no params are provided entire EP gets unapproved.
        When providing params, give one of these:

        * `hcp_objectives : Bool`
        * `hcp_objectives_ids : [Int]` - list of ids

        *Ignore body params table that maybe below this action, none of those are used.*

        ---
        """
        eplan = self.get_object()

        hcp_items = request.data.get('hcp_items')
        hcp_items_ids = request.data.get('hcp_items_ids')

        if hcp_items:
            for hcp_item in eplan.hcp_items.all():
                hcp_item.unapprove()
            eplan.unapprove()

        if hcp_items_ids:
            for hcp_item in hcp_items_ids:
                eplan.hcp_items.get(id=hcp_item).unapprove()
            if eplan.hcp_items.filter(approved=False).exists():
                eplan.unapprove()

        return Response(self.get_serializer(eplan).data)


class CurrentUserView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
