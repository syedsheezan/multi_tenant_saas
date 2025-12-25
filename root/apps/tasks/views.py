from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOrgMember, IsOrgAdminOrOwner
from apps.tenants.response import success_response, error_response
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskListCreateView(APIView):
    permission_classes = [IsOrgMember]

    @swagger_auto_schema(
        operation_summary="List tasks in a project",
        tags=["Tasks"],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, project_id=None):
        org = request.organization
        tasks = Task.objects.filter(project_id=project_id, organization=org, is_archived=False)
        return success_response(TaskSerializer(tasks, many=True).data, "Tasks fetched", status_code=status.HTTP_200_OK,request=request) #status.HTTP_200_OK

    @swagger_auto_schema(
        operation_summary="Create new task",
        tags=["Tasks"],
        request_body=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request, project_id=None):
        org = request.organization
        user = request.user

        data = request.data.copy()
        data["project"] = project_id
        # data["organization"] = str(org.id)

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save(created_by=user,organization=org)
            return success_response(TaskSerializer(task).data, "Task created", status.HTTP_201_CREATED, request)

        return error_response(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST, request)

class TaskDetailView(APIView):
    permission_classes = [IsOrgMember]

    @swagger_auto_schema(
        operation_summary="Get task details",
        tags=["Tasks"]
    )
    def get(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        return success_response(TaskSerializer(task).data, "Task fetched", request)

    @swagger_auto_schema(
        operation_summary="Update task",
        tags=["Tasks"],
        request_body=TaskSerializer
    )
    def patch(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Task updated", request)

        return error_response(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST, request)

    @swagger_auto_schema(
        operation_summary="Delete task",
        tags=["Tasks"]
    )
    def delete(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task.is_archived = True
        task.save()
        return success_response({}, "Task deleted", status.HTTP_204_NO_CONTENT, request)
