"""interactions URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from interactionscore import views as core_views


router = routers.DefaultRouter()
router.register(r'affiliate-groups', core_views.AffiliateGroupViewSet)
router.register(r'engagement-plans', core_views.EngagementPlanViewSet)
router.register(r'hcps', core_views.HCPViewSet)
router.register(r'interactions', core_views.InteractionViewSet)
router.register(r'projects', core_views.ProjectViewSet)
router.register(r'therapeutic-areas', core_views.TherapeuticAreaViewSet)
router.register(r'resources', core_views.ResourceViewSet)
router.register(r'interaction-outcomes', core_views.InteractionOutcomeViewSet)
router.register(r'hcp-objectives', core_views.HCPObjectiveViewSet)

urlpatterns = [
    path('djadmin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),
    path('api/v1/', include([
        path('token/obtain/', obtain_jwt_token),
        path('token/refresh/', refresh_jwt_token),
        path('token/verify/', verify_jwt_token),
        path('self/', core_views.CurrentUserView.as_view(), name='users-current'),
        path('docs/', include_docs_urls(title='My API title', public=False)),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ] + router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
