from django.utils import timezone
from rest_framework import viewsets, status
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
    HCP,
    AffiliateGroup,
    TherapeuticArea,
    Resource,
    Project,
    Interaction,
    InteractionOutcome,
    HCPObjective,
)
from .serializers import (
    AffiliateGroupSerializer,
    ProjectSerializer,
    TherapeuticAreaSerializer,
    ResourceSerializer,
    EngagementPlanSerializer,
    HCPSerializer,
    InteractionSerializer,
    InteractionOutcomeSerializer,
    UserSerializer,
    HCPObjectiveSerializer,
)


class AffiliateGroupViewSet(viewsets.ModelViewSet):
    queryset = AffiliateGroup.objects.all()
    serializer_class = AffiliateGroupSerializer
    permission_classes = (IsAuthenticated,)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)


class TherapeuticAreaViewSet(viewsets.ModelViewSet):
    queryset = TherapeuticArea.objects.all()
    serializer_class = TherapeuticAreaSerializer
    permission_classes = (IsAuthenticated,)


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated,)


class InteractionOutcomeViewSet(viewsets.ModelViewSet):
    queryset = InteractionOutcome.objects.all()
    serializer_class = InteractionOutcomeSerializer
    permission_classes = (IsAuthenticated,)


class HCPViewSet(viewsets.ModelViewSet):
    queryset = HCP.objects.all()
    serializer_class = HCPSerializer
    permission_classes = (IsAuthenticated,)


class HCPObjectiveViewSet(viewsets.ModelViewSet):
    queryset = HCPObjective.objects.all()
    serializer_class = HCPObjectiveSerializer
    permission_classes = (IsAuthenticated,)


class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = (IsAuthenticated,)


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
                if obj.year.year != timezone.now().year:
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
