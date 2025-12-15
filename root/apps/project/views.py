from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import Project
from .serializers import ProjectSerializer
from apps.tenants.models import Organization, OrganizationMembership


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # 1️⃣ Tenant explicitly passed in body
        tenant = serializer.validated_data.pop("tenant", None)

        # 2️⃣ If tenant is provided in body → ONLY superuser allowed
        if tenant:
            if not user.is_superuser:
                raise PermissionDenied(
                    "Only superusers can specify tenant explicitly."
                )

        # 3️⃣ If tenant not provided → try header (optional support)
        if not tenant:
            org_id = (
                self.request.headers.get("X-ORGANIZATION-ID")
                or self.request.META.get("HTTP_X_ORGANIZATION_ID")
            )
            if org_id:
                tenant = Organization.objects.filter(id=org_id).first()

        # 4️⃣ Hard stop if still missing
        if not tenant:
            raise ValidationError({
                "tenant": "Tenant is required. Provide tenant in body (superuser) or X-ORGANIZATION-ID header."
            })

        # 5️⃣ Authorization check for non-superusers
        if not user.is_superuser:
            allowed = OrganizationMembership.objects.filter(
                user=user,
                organization=tenant,
                is_active=True,
                role__in=[
                    OrganizationMembership.ROLE_OWNER,
                    OrganizationMembership.ROLE_ADMIN,
                ],
            ).exists()

            if not allowed:
                raise PermissionDenied(
                    "You are not authorized to create projects for this organization."
                )

        # 6️⃣ Create project
        serializer.save(
            owner=user,
            tenant=tenant
        )
