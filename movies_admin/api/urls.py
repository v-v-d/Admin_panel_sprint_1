from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.v1.urls import router as v1_router

schema_view = get_schema_view(
   openapi.Info(
      title='Movies API',
      default_version='v1',
      description='Movies API docs',
   ),
   public=True,
   permission_classes=(permissions.AllowAny, ),
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
