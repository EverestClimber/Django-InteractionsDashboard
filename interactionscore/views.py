from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
)

from .models import (
    EngagementPlan, EngagementPlanPerms,
)
from .serializers import (
    EngagementPlanSerializer,
)


class EngagementPlanViewSet(viewsets.ModelViewSet):
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
            self.request.user.has_perm(EngagementPlanPerms.list_all_ep.name)
        ):
            return qs
        # list_own_ag_ep perm allows listing EPs from same AG as user
        if self.request.user.has_perm(EngagementPlanPerms.list_own_ag_ep.name):
            return qs.filter(user__affiliate_groups__in=self.request.user.affiliate_groups.all())
        # by default a user only has access to his own EPs
        return qs.filter(user=self.request.user)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)

        user = self.request.user

        if self.action in {'list', 'retrieve'}:  # restricted by get_queryset above
            return  # allow

        if self.action in {'approve', 'unapprove'}:
            # users with approve_all_ep perm can approve all EPs
            if user.has_perm(EngagementPlanPerms.approve_all_ep.name):
                return  # allow
            # users with approve_own_ag_ep can only approve EPs with same Affiliate Group
            if user.has_perm(EngagementPlanPerms.approve_own_ag_ep.name):
                if (obj.affiliate_groups.all() & user.affiliate_groups.all()).exists():
                    return  # allow
            # by default deny (raises exc)
            self.permission_denied(request, 'User does not have required permission')

        if self.action in {'destroy', 'update', 'partial_update'}:
            if user.has_perm('interactionscore.change_engagementplan'):
                return  # allow
            if user.has_perm(EngagementPlanPerms.change_own_current_ep.name):
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
        self.get_object().approve()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='unapprove')
    def unapprove(self, request, pk=None):
        self.get_object().unapprove()
        return Response(status=status.HTTP_200_OK)
