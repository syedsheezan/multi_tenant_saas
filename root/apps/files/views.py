from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404

from .models import File
from .serializers import FileUploadSerializer
from apps.tenants.models import Organization
from apps.tenants.response import success_response, error_response
from apps.tenants.permissions import IsTenantProvided
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantProvided]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Upload file for project/task",
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Upload file",
            ),
            openapi.Parameter(
                name="project",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="task",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
    )
    def post(self, request):
        try:
            org_id = request.headers.get("X-ORGANIZATION-ID")
            organization = get_object_or_404(Organization, id=org_id)

            serializer = FileUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return error_response(
                    "File is required",
                    "Validation error",
                    status.HTTP_400_BAD_REQUEST,
                    request
                )

            file_obj = File.objects.create(
                organization=organization,
                project=serializer.validated_data.get("project"),
                task=serializer.validated_data.get("task"),
                uploaded_by=request.user,
                file=uploaded_file,
                original_name=uploaded_file.name,
                size=uploaded_file.size,
                content_type=uploaded_file.content_type,
            )

            return success_response(
                {
                    "file_id": str(file_obj.id),
                    "name": file_obj.original_name,
                },
                "File uploaded successfully",
                status.HTTP_201_CREATED,
                request
            )

        except Exception as e:
            return error_response(
                str(e),
                "File upload failed",
                status.HTTP_400_BAD_REQUEST,
                request
            )



class FileListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantProvided]

    def get(self, request):
        try:
            org = request.organization

            project_id = request.query_params.get("project_id")
            task_id = request.query_params.get("task_id")

            files = File.objects.filter(organization=org)

            if project_id:
                files = files.filter(project_id=project_id)

            if task_id:
                files = files.filter(task_id=task_id)

            data = [
                {
                    "id": str(f.id),
                    "name": f.original_name,
                    "uploaded_by": f.uploaded_by.email,
                    "size": f.size,
                    "content_type": f.content_type,
                    "created_at": f.created_at,
                }
                for f in files
            ]

            return success_response(
                data,
                "Files fetched successfully",
                request=request
            )

        except Exception as e:
            return error_response(
                str(e),
                "Failed to fetch files",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                request
            )


# class FileUploadView(APIView):
#     permission_classes = [permissions.IsAuthenticated, IsTenantProvided]

#     def post(self, request):
#         try:
#             org_id = request.headers.get("X-ORGANIZATION-ID")
#             organization = get_object_or_404(Organization, id=org_id)

#             serializer = FileUploadSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)

#             uploaded_file = request.FILES.get("file")

#             file_obj = File.objects.create(
#                 organization=organization,
#                 project=serializer.validated_data.get("project"),
#                 task=serializer.validated_data.get("task"),
#                 uploaded_by=request.user,
#                 file=uploaded_file,
#                 original_name=uploaded_file.name,
#                 size=uploaded_file.size,
#                 content_type=uploaded_file.content_type,
#             )

#             # 🔔 Notification (future)
#             # 📜 Audit (future)

#             return success_response(
#                 {
#                     "file_id": str(file_obj.id),
#                     "name": file_obj.original_name
#                 },
#                 "File uploaded successfully",
#                 status.HTTP_201_CREATED,
#                 request
#             )

#         except Exception as e:
#             return error_response(
#                 str(e),
#                 "File upload failed",
#                 status.HTTP_400_BAD_REQUEST,
#                 request
#             )

