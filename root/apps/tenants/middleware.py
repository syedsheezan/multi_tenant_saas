from django.utils.deprecation import MiddlewareMixin
from .models import Organization
from django.core.exceptions import PermissionDenied

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        org_id = request.headers.get("X-ORGANIZATION-ID")

        if not org_id:
            request.organization = None
            return

        try:
            request.organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise PermissionDenied("Invalid organization")
