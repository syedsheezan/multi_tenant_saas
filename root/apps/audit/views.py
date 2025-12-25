from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.tenants.response import success_response


class AuditLogListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org_id = request.headers.get("X-ORGANIZATION-ID")

        logs = AuditLog.objects.filter(organization_id=org_id)

        serializer = AuditLogSerializer(logs, many=True)

        return success_response(
            serializer.data,
            "Audit logs fetched",
            request=request
        )
