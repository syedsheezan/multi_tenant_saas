from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsProjectOwnerOrReadOnly

from root.apps.project import models

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','description','slug']

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant is None:
            return Project.objects.none()
        qs = Project.objects.filter(tenant=tenant, archived=False)
        # if user is staff/admin show all
        if self.request.user.is_staff or getattr(self.request.user,'is_admin',False):
            return qs
        # show public projects + projects where user is a member
        return qs.filter(models.Q(is_public=True) | models.Q(memberships__user=self.request.user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, tenant=self.request.tenant)
        # trigger notification / celery task if needed

