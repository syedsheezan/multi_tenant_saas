from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from .tasks import send_notification_email, dispatch_push_notification
from apps.tenants.response import success_response, error_response
from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["Notifications"], responses={200: NotificationSerializer(many=True)})
    def get(self, request):
        # tenant-scoped: filter by request.organization if set
        org = getattr(request, "organization", None)
        qs = Notification.objects.filter(recipient=request.user)
        if org:
            qs = qs.filter(organization=org)
        serializer = NotificationSerializer(qs, many=True)
        return success_response(serializer.data, "Notifications fetched", request=request)

class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["Notifications"], request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"ids": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))}
    ), responses={200: "Marked"})
    def post(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return error_response("No ids provided", "ids required", status.HTTP_400_BAD_REQUEST, request=request)
        updated = Notification.objects.filter(id__in=ids, recipient=request.user).update(is_read=True)
        return success_response({"updated": updated}, "Notifications marked read", request=request)

class NotificationMarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["Notifications"], responses={200: "Marked all"})
    def post(self, request):
        org = getattr(request, "organization", None)
        qs = Notification.objects.filter(recipient=request.user)
        if org:
            qs = qs.filter(organization=org)
        updated = qs.update(is_read=True)
        return success_response({"updated": updated}, "All notifications marked read", request=request)

class NotificationCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["Notifications"], responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={"unread_count": openapi.Schema(type=openapi.TYPE_INTEGER)})})
    def get(self, request):
        org = getattr(request, "organization", None)
        qs = Notification.objects.filter(recipient=request.user, is_read=False)
        if org:
            qs = qs.filter(organization=org)
        count = qs.count()
        return success_response({"unread_count": count}, "Unread count", request=request)
