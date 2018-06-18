from rest_framework import viewsets, status
from rest_framework import permissions
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
from .permissions import (
    OwnsResource
)


class EngagementPlanViewSet(viewsets.ModelViewSet):
    queryset = EngagementPlan.objects.all()
    serializer_class = EngagementPlanSerializer
    permission_classes = (
        IsAuthenticated,
        OwnsResource,
    )

    def get_queryset(self):
        qs = super().get_queryset()

        if (
            self.request.user.is_staff or
            self.request.user.has_perm(EngagementPlanPerms.list_all_ep.name)
        ):
            return qs

        if self.request.user.has_perm(EngagementPlanPerms.list_own_ag_ep.name):
            return qs.filter(user__affiliate_groups__in=self.request.user.affiliate_groups.all())

    @action(methods=['post'], detail=True, url_path='approve')
    def approve(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
