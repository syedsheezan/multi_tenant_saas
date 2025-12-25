# core/urls.py (top)
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

# 🔥 CUSTOM SWAGGER HEADER
organization_header = openapi.Parameter(
    'X-ORGANIZATION-ID',
    openapi.IN_HEADER,
    description="Organization UUID (Tenant ID)",
    type=openapi.TYPE_STRING,
    required=False,
)

# core/urls.py (below)
schema_view = get_schema_view(
   openapi.Info(
      title="Tenant PMS API",
      default_version='v1',
      description="API docs for Tenant PMS",
      contact=openapi.Contact(email="dev@yourorg.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ... your existing url patterns

    path('admin/', admin.site.urls),

    path('users', include('apps.users.urls')),
    path('tenants', include('apps.tenants.urls')),
    path('tasks', include('apps.tasks.urls')),
    path('project', include('apps.project.urls')),
    path('notifications', include('apps.notifications.urls')),
    path("auditlogs", include("apps.audit.urls")),
    path("", include("apps.files.urls")),

      # Swagger / Redoc
    path('api/docs/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)