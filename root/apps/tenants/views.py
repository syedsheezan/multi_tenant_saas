from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Organization, OrganizationMembership, Plan
from .serializers import (
    OrganizationSerializer,
    OrganizationMembershipSerializer,
    PlanSerializer
)
from .permissions import IsTenantProvided, IsOrgOwnerOrAdmin
from .response import success_response, error_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .response import success_response, error_response
from django.contrib.auth.models import User

class PlanListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = []

    @swagger_auto_schema(
        operation_summary="Get Subscription Plans",
        tags=["Plans"],
        responses={200: PlanSerializer(many=True)}
    )

    def get(self, request):
        try:
            queryset = Plan.objects.all()
            serializer = PlanSerializer(queryset, many=True)
            return success_response(serializer.data, "Plans fetched successfully", request=request)
        except Exception as e:
            return error_response(str(e), "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR, request)


class OrganizationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = []

    @swagger_auto_schema(
        operation_summary="List My Organizations",
        tags=["Organizations"],
        responses={200: OrganizationSerializer(many=True)}
    )

    def get(self, request):
        try:
            user = request.user
            if user.is_superuser:
                orgs = Organization.objects.all()
            else:
                orgs = Organization.objects.filter(memberships__user=user).distinct()

            serializer = OrganizationSerializer(orgs, many=True)
            return success_response(serializer.data, "Organizations fetched successfully", request=request)
        except Exception as e:
            return error_response(str(e), "Failed to fetch organizations", status.HTTP_500_INTERNAL_SERVER_ERROR, request)

    @swagger_auto_schema(
        operation_summary="Create Organization",
        tags=["Organizations"],
        request_body=OrganizationSerializer,
        responses={201: OrganizationSerializer}
    )

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            org = serializer.save(owner=request.user)
            OrganizationMembership.objects.create(
                user=request.user,
                organization=org,
                role=OrganizationMembership.ROLE_OWNER
            )
            return success_response(serializer.data, "Organization created successfully", status.HTTP_201_CREATED, request)

        return error_response(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST, request)


class OrganizationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrgOwnerOrAdmin]
    # permission_classes = []

    # ---------------------- GET ----------------------
    @swagger_auto_schema(
        operation_summary="Get Organization Details",
        tags=["Organizations"],
        responses={200: OrganizationSerializer}
    )
    def get(self, request, pk=None):
        try:
            org = get_object_or_404(Organization, pk=pk)
            serializer = OrganizationSerializer(org)
            return success_response(serializer.data, "Organization details fetched", request=request)
        except Exception as e:
            return error_response(str(e), "Organization not found", status.HTTP_404_NOT_FOUND, request)

    # ---------------------- PUT (Full Update) ----------------------
    @swagger_auto_schema(
        operation_summary="Update Organization (Full Update)",
        tags=["Organizations"],
        request_body=OrganizationSerializer,
        responses={200: OrganizationSerializer}
    )
    def put(self, request, pk=None):
        try:
            org = get_object_or_404(Organization, pk=pk)
            serializer = OrganizationSerializer(org, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Organization updated successfully", request=request)

            return error_response(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST, request)

        except Exception as e:
            return error_response(str(e), "Update failed", status.HTTP_500_INTERNAL_SERVER_ERROR, request)

    # ---------------------- PATCH (Partial Update) ----------------------
    @swagger_auto_schema(
        operation_summary="Update Organization (Partial Update)",
        tags=["Organizations"],
        request_body=OrganizationSerializer,
        responses={200: OrganizationSerializer}
    )
    def patch(self, request, pk=None):
        try:
            org = get_object_or_404(Organization, pk=pk)
            serializer = OrganizationSerializer(org, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Organization partially updated", request=request)

            return error_response(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST, request)

        except Exception as e:
            return error_response(str(e), "Partial update failed", status.HTTP_500_INTERNAL_SERVER_ERROR, request)

    # ---------------------- DELETE ----------------------
    @swagger_auto_schema(
        operation_summary="Delete Organization",
        tags=["Organizations"],
        responses={204: "Deleted Successfully"}
    )
    def delete(self, request, pk=None):
        try:
            org = get_object_or_404(Organization, pk=pk)
            org.delete()

            return success_response(
                data={},
                message="Organization deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT,
                request=request
            )

        except Exception as e:
            return error_response(str(e), "Delete failed", status.HTTP_500_INTERNAL_SERVER_ERROR, request)


# class OrganizationInviteView(APIView):
#     permission_classes = [permissions.IsAuthenticated,IsTenantProvided, IsOrgOwnerOrAdmin]
#     # permission_classes = []

#     @swagger_auto_schema(
#         operation_summary="Invite User to Organization",
#         tags=["Organizations"],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=["user_uuid"],
#             properties={
#                 "user_uuid": openapi.Schema(type=openapi.TYPE_STRING),
#                 "role": openapi.Schema(type=openapi.TYPE_STRING, default="member"),
#             }
#         ),
#         responses={201: OrganizationMembershipSerializer}
#     )

#     def post(self, request, org_id):
#         try:
#             org = get_object_or_404(Organization, pk=org_id)
#             # user_id = request.data.get("user_id")
#             user_uuid = request.data.get("user_uuid")
#             role = request.data.get("role", OrganizationMembership.ROLE_MEMBER)

#             from django.contrib.auth import get_user_model
#             User = get_user_model()

#             try:
#                 user = User.objects.get(id=user_uuid) # yaha id
#             except User.DoesNotExist:
#                 return error_response("User not found", status_code=status.HTTP_404_NOT_FOUND, request=request)
            
#             membership, created = OrganizationMembership.objects.get_or_create(
#                 user=user, organization=org, defaults={"role": role}
#             )

#             serializer = OrganizationMembershipSerializer(membership)
#             return success_response(serializer.data,
#                                     "User invited successfully" if created else "User already a member",
#                                     status.HTTP_201_CREATED,
#                                     request=request)

#         except Exception as e:
#             return error_response(str(e), "Failed to invite user", status.HTTP_500_INTERNAL_SERVER_ERROR, request)

class OrganizationInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantProvided, IsOrgOwnerOrAdmin]

    @swagger_auto_schema(
        operation_summary="Invite User to Organization",
        tags=["Organizations"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_uuid"],
            properties={
                "user_uuid": openapi.Schema(type=openapi.TYPE_STRING),
                "role": openapi.Schema(type=openapi.TYPE_STRING, default="member"),
            }
        )
    )
    def post(self, request, org_id):
        try:
            org = get_object_or_404(Organization, pk=org_id)

            user_uuid = request.data.get("user_uuid")

            from django.contrib.auth import get_user_model
            User = get_user_model()

            user = get_object_or_404(User, id=user_uuid)

            # ================= FIX =================
            # ❌ NO OrganizationMembership here
            # ✅ Only create Invitation
            from apps.tenants.models import Invitation

            # Invitation.objects.create(
            invitation = Invitation.objects.create(
                email=user.email,
                invited_user=user, 
                organization=org,
                invited_by=request.user,
                role=request.data.get("role", "member")
            )
            # =======================================

            from apps.audit.services import log_audit
            log_audit(
                organization=org,
                actor=request.user,
                action="invite_sent",
                object_type="Invitation",
                object_id=invitation.id,
                message=f"Invited {user.email} to organization",
                metadata={"email": user.email}
            )

            return success_response(
                {},
                "Invitation sent successfully",
                status.HTTP_201_CREATED,
                request=request
            )

        except Exception as e:
            return error_response(str(e), "Failed to invite user", status.HTTP_500_INTERNAL_SERVER_ERROR, request)


class InvitationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List My Pending Invitations",
        tags=["Invitations"],
        responses={200: "List of invitations"}
    )
    def get(self, request):
        from apps.tenants.models import Invitation
        from apps.audit.services import log_audit

        invitations = Invitation.objects.filter(
            email=request.user.email,
            accepted=False
        )

        data = [
            {
                "invite_id": str(inv.id),  # 🔥 THIS IS IMPORTANT
                "organization": inv.organization.name,
                "organization_id": str(inv.organization.id),
                "invited_by": inv.invited_by.email if inv.invited_by else None,
                "created_at": inv.created_at,
            }
            for inv in invitations
        ]

        return success_response(
            data,
            "Pending invitations fetched",
            request=request
        )
    
class AcceptInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Accept Organization Invitation",
        tags=["Invitations"]
    )
    def post(self, request, invite_id):
        from apps.tenants.models import Invitation, OrganizationMembership
        from apps.audit.services import log_audit 

        invitation = get_object_or_404(
            Invitation,
            id=invite_id,
            email=request.user.email,
            accepted=False
        )

        # Create membership
        OrganizationMembership.objects.create(
            user=request.user,
            organization=invitation.organization,
            # role=OrganizationMembership.ROLE_MEMBER
            role=invitation.role
        )

        # Mark invitation accepted
        invitation.accepted = True
        invitation.save()

        log_audit(
            organization=invitation.organization,
            actor=request.user,
            action="invite_accepted",
            object_type="Invitation",
            object_id=invitation.id,
            message=f"{request.user.email} accepted invitation"
        )


        return success_response(
            {},
            "Invitation accepted successfully",
            status.HTTP_200_OK,
            request
        )

class RejectInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, invite_id):
        from apps.tenants.models import Invitation
        from apps.audit.services import log_audit

        invitation = get_object_or_404(
            Invitation,
            id=invite_id,
            email=request.user.email,
            accepted=False
        )

        log_audit(
            organization=invitation.organization,
            actor=request.user,
            action="invite_rejected",
            object_type="Invitation",
            object_id=invitation.id,
            message=f"{request.user.email} rejected invitation"
        )

        invitation.delete()

        return success_response(
            {},
            "Invitation rejected",
            status.HTTP_200_OK,
            request
        )



class MembershipListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantProvided]
    # permission_classes = []

    @swagger_auto_schema(
        operation_summary="List Members of an Organization",
        tags=["Organizations - Members"],
        manual_parameters=[
            openapi.Parameter(
                "X-ORGANIZATION-ID",
                openapi.IN_HEADER,
                description="Organization ID",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: OrganizationMembershipSerializer(many=True)}
    )

    def get(self, request):
        try:
            org = request.organization
            memberships = OrganizationMembership.objects.filter(organization=org)
            serializer = OrganizationMembershipSerializer(memberships, many=True)
            return success_response(serializer.data, "Members fetched successfully", request=request)
        except Exception as e:
            return error_response(str(e), "Failed to fetch members", status.HTTP_500_INTERNAL_SERVER_ERROR, request)

class OrganizationMemberRemoveView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsTenantProvided,
        IsOrgOwnerOrAdmin
    ]

    def delete(self, request, membership_id):
        try:
            membership = get_object_or_404(
                OrganizationMembership,
                id=membership_id,
                organization=request.organization,
                is_active=True
            )

            # ❌ Owner ko remove nahi kar sakte
            if membership.role == OrganizationMembership.ROLE_OWNER:
                return error_response(
                    "Owner cannot be removed",
                    status.HTTP_400_BAD_REQUEST,
                    request
                )

            membership.is_active = False
            membership.save()

            return success_response(
                {},
                "Member removed successfully",
                request=request
            )

        except Exception as e:
            return error_response(
                str(e),
                "Failed to remove member",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                request
            )