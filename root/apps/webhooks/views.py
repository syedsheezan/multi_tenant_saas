# apps/webhooks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import WebhookSubscription
from .serializers import WebhookSubscriptionSerializer

class IsTenantMember(permissions.BasePermission):
    """
    Ensure the request has request.organization (middleware must set it)
    and that the object belongs to the same organization.
    """

    def has_permission(self, request, view):
        return getattr(request, "user", None) and getattr(request, "organization", None)

    def has_object_permission(self, request, view, obj):
        return obj.organization == request.organization


class WebhookListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get(self, request):
        qs = WebhookSubscription.objects.filter(organization=request.organization, is_active=True)
        serializer = WebhookSubscriptionSerializer(qs, many=True)
        return Response({
            "ok": True,
            "status": status.HTTP_200_OK,
            "message": "Webhook subscriptions fetched",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WebhookSubscriptionSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({
                "ok": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Validation failed",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        out = WebhookSubscriptionSerializer(obj).data
        return Response({
            "ok": True,
            "status": status.HTTP_201_CREATED,
            "message": "Webhook subscription created",
            "data": out
        }, status=status.HTTP_201_CREATED)


class WebhookDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_object(self, pk, organization):
        # returns active or raises 404
        obj = get_object_or_404(WebhookSubscription, pk=pk, organization=organization)
        return obj

    def get(self, request, pk):
        obj = self.get_object(pk, request.organization)
        serializer = WebhookSubscriptionSerializer(obj)
        return Response({
            "ok": True,
            "status": status.HTTP_200_OK,
            "message": "Webhook fetched",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = self.get_object(pk, request.organization)
        serializer = WebhookSubscriptionSerializer(obj, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({
                "ok": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Validation failed",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        return Response({
            "ok": True,
            "status": status.HTTP_200_OK,
            "message": "Webhook fully updated",
            "data": WebhookSubscriptionSerializer(obj).data
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        obj = self.get_object(pk, request.organization)
        serializer = WebhookSubscriptionSerializer(obj, data=request.data, partial=True, context={"request": request})
        if not serializer.is_valid():
            return Response({
                "ok": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Validation failed",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        return Response({
            "ok": True,
            "status": status.HTTP_200_OK,
            "message": "Webhook partially updated",
            "data": WebhookSubscriptionSerializer(obj).data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        obj = self.get_object(pk, request.organization)
        # Soft delete: mark inactive
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])
        return Response({
            "ok": True,
            "status": status.HTTP_200_OK,
            "message": "Webhook disabled",
            "data": {"id": obj.id}
        }, status=status.HTTP_200_OK)


