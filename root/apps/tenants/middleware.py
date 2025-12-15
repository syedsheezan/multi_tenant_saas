# apps/tenants/middleware.py
from django.apps import apps
from django.utils.deprecation import MiddlewareMixin

class TenantMiddleware(MiddlewareMixin):
    """
    Read tenant identifier from header X-ORGANIZATION-ID (or query param)
    and attach the Organization instance on request.tenant (or None).
    """

    HEADER_NAME = "HTTP_X_ORGANIZATION_ID"  # Django prefixes HTTP_ for headers in request.META

    def process_request(self, request):
        # preferred: header first
        org_id = None
        # 1) look in headers
        org_id = request.META.get(self.HEADER_NAME)
        # 2) fallback to query param
        if not org_id:
            org_id = request.GET.get("organization_id") or request.GET.get("org_id") or request.GET.get("tenant")
        # 3) fallback to body (not safe for GET) — we do not read body here

        if not org_id:
            request.tenant = None
            return None

        # Resolve Organization model lazily
        Organization = apps.get_model("tenants", "Organization")
        try:
            org = Organization.objects.filter(id=org_id).first()
        except Exception:
            org = None
        request.tenant = org
        return None
