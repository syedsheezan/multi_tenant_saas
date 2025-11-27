from django.urls import path
from .views import (
    PlanListView,
    OrganizationListCreateView,
    OrganizationDetailView,
    MembershipListView,
    OrganizationInviteView
)

urlpatterns = [
    # Plans
    path("plans", PlanListView.as_view(), name="plans-list"),

    # Organizations
    path("organizations", OrganizationListCreateView.as_view(), name="organizations-list"),
    path("organizations/<uuid:pk>", OrganizationDetailView.as_view(), name="organizations-detail"),

    # Memberships (needs X-ORGANIZATION-ID header)
    path("memberships", MembershipListView.as_view(), name="memberships-list"),

    # Invite user inside an organization
    path("organizations/<uuid:org_id>/invite", OrganizationInviteView.as_view(), name="organizations-invite"),
]
