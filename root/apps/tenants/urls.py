from django.urls import path
from .views import (
    OrganizationMemberRemoveView,
    PlanListView,
    OrganizationListCreateView,
    OrganizationDetailView,
    MembershipListView,
    OrganizationInviteView,
    RejectInvitationView,AcceptInvitationView,InvitationListView
)
urlpatterns = [
    # Plans
    path("plans", PlanListView.as_view(), name="plans-list"),

    # Organizations
    path("organizations", OrganizationListCreateView.as_view(), name="organizations-list"),
    path("organizations/<uuid:pk>", OrganizationDetailView.as_view(), name="organizations-detail"),

    # Memberships (needs X-ORGANIZATION-ID header)
    path("memberships", MembershipListView.as_view(), name="memberships-list"),
    path("tenantsmemberships/<uuid:membership_id>/",OrganizationMemberRemoveView.as_view(),),


    # Invite user inside an organization
    path("organizations/<uuid:org_id>/invite", OrganizationInviteView.as_view(), name="organizations-invite"),

    path("organizations/invitations", InvitationListView.as_view()),
    path("organizations/invitations/<uuid:invite_id>/accept/", AcceptInvitationView.as_view()),
    path("organizations/invitations/<uuid:invite_id>/reject/", RejectInvitationView.as_view()),

]
#e61badd5-9a2e-4dff-bf46-2187ffac2b79
