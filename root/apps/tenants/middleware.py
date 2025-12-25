from django.utils.deprecation import MiddlewareMixin
from .models import Organization
from django.core.exceptions import PermissionDenied

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        org_id = request.headers.get("X-ORGANIZATION-ID")
        
        # If no header provided
        if not org_id:
            request.organization = None
            request.tenant = None
            return

        # Validate organization
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise PermissionDenied("Invalid organization")

        # Set both attributes
        request.organization = organization
        request.tenant = organization   # <- IMPORTANT LINE
