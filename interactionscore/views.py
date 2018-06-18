from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    EngagementPlan,
)
from .serializers import (
    EngagementPlanSerializer,
)


class EngagementPlanViewSet(viewsets.ModelViewSet):
    queryset = EngagementPlan.objects.all()
    serializer_class = EngagementPlanSerializer

    @action(methods=['post'], detail=True, url_path='approve')
    def approve(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
