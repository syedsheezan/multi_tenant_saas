from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg import openapi

TENANT_HEADER = openapi.Parameter(
    "X-ORGANIZATION-ID",
    openapi.IN_HEADER,
    description="Organization (Tenant) UUID",
    type=openapi.TYPE_STRING,
    format="uuid",
    required=False,
)

class TenantAutoSchema(SwaggerAutoSchema):
    def get_manual_parameters(self, *args, **kwargs):
        params = super().get_manual_parameters(*args, **kwargs)
        if not any(p.name == "X-ORGANIZATION-ID" for p in params):
            params.append(TENANT_HEADER)
        return params
