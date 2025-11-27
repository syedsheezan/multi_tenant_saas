# apps/users/views.py
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response  # only used by drf-yasg examples, logic uses custom_response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    AdminUserSerializer,
    CustomTokenObtainPairSerializer,
)
from .permissions import IsAdminOrSelf
from root.utils import custom_response

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# drf-yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class CustomTokenObtainView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Accepts {"username": "...", "password":"...", "org_id": <optional>}
    Returns refresh & access tokens. If org_id provided and user is a member,
    the returned access token includes org_id & role claims.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Obtain JWT tokens. Optionally include org_id to scope token to an organization.",
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: openapi.Response("Token pair", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'org_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                }
            )),
            401: "Invalid credentials",
            400: "Bad request"
        }
    )
    def post(self, request, *args, **kwargs):
        # delegate to SimpleJWT serializer logic, then place into custom_response
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return custom_response(
            message="Logged in successfully.",
            data=data,
            status_code=status.HTTP_200_OK,
            request=request
        )


# ---------------------------
# /api/auth/users/  -> list (GET) / create (POST)
# ---------------------------
class UsersListCreateAPIView(APIView):
    """
    GET  -> list users (admin/staff only)
    POST -> register (public)
    """
    permission_classes = [permissions.AllowAny]  # POST allowed; GET checked inside

    @swagger_auto_schema(
        operation_description="List all users (admin only).",
        responses={
            200: openapi.Response(
                "List of users",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)  # serializer used at runtime
                )
            ),
            403: "Not permitted"
        }
    )
    def get(self, request, *args, **kwargs):
        # Only admins/staff may list users
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return custom_response("Not permitted.", status_code=status.HTTP_403_FORBIDDEN, request=request, error="forbidden")

        qs = User.objects.all().order_by("id")
        serializer = AdminUserSerializer(qs, many=True, context={"request": request})
        return custom_response("User list fetched.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)

    @swagger_auto_schema(
        operation_description="Register a new user (public).",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response("User registered", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: "Validation error"
        }
    )
    def post(self, request, *args, **kwargs):
        # public registration
        serializer = RegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        out_serializer = UserSerializer(user, context={"request": request})
        return custom_response("User created.", data=out_serializer.data, status_code=status.HTTP_201_CREATED, request=request)


# ---------------------------
# /api/auth/users/{pk}/  -> retrieve / put / patch / delete
# ---------------------------
class UserDetailAPIView(APIView):
    """
    GET    -> retrieve user (admin or the user themself)
    PUT    -> full update (admin or self)
    PATCH  -> partial update (admin or self)
    DELETE -> delete user (admin or self)
    """
    permission_classes = [permissions.IsAuthenticated]  # object-level checked below

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def check_object_permissions_custom(self, request, obj):
        # use IsAdminOrSelf to check object-level permission in addition to IsAuthenticated
        perm = IsAdminOrSelf()
        return perm.has_object_permission(request, self, obj)

    @swagger_auto_schema(
        operation_description="Retrieve a user by ID (admin or the user themself).",
        responses={200: UserSerializer}
    )
    def get(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        if not self.check_object_permissions_custom(request, user):
            return custom_response("Not permitted.", status_code=status.HTTP_403_FORBIDDEN, request=request, error="forbidden")

        # choose serializer depending on viewer privileges
        if request.user.is_staff or request.user.is_superuser:
            serializer = AdminUserSerializer(user, context={"request": request})
        else:
            serializer = UserSerializer(user, context={"request": request})
        return custom_response("User retrieved.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)

    @swagger_auto_schema(
        operation_description="Update a user fully (admin or self).",
        request_body=AdminUserSerializer,
        responses={200: AdminUserSerializer, 400: "Validation error", 403: "Not permitted"}
    )
    def put(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        if not self.check_object_permissions_custom(request, user):
            return custom_response("Not permitted.", status_code=status.HTTP_403_FORBIDDEN, request=request, error="forbidden")

        # admin may edit with AdminUserSerializer; self uses UserSerializer
        if request.user.is_staff or request.user.is_superuser:
            serializer = AdminUserSerializer(user, data=request.data, context={"request": request})
        else:
            serializer = UserSerializer(user, data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response("User updated.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)

    @swagger_auto_schema(
        operation_description="Partially update a user (admin or self).",
        request_body=AdminUserSerializer,
        responses={200: AdminUserSerializer, 400: "Validation error", 403: "Not permitted"}
    )
    def patch(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        if not self.check_object_permissions_custom(request, user):
            return custom_response("Not permitted.", status_code=status.HTTP_403_FORBIDDEN, request=request, error="forbidden")

        if request.user.is_staff or request.user.is_superuser:
            serializer = AdminUserSerializer(user, data=request.data, partial=True, context={"request": request})
        else:
            serializer = UserSerializer(user, data=request.data, partial=True, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response("User partially updated.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)

    @swagger_auto_schema(
        operation_description="Delete a user (admin or self).",
        responses={204: "Deleted", 403: "Not permitted"}
    )
    def delete(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        if not self.check_object_permissions_custom(request, user):
            return custom_response("Not permitted.", status_code=status.HTTP_403_FORBIDDEN, request=request, error="forbidden")

        # perform delete (consider soft-delete in production)
        user.delete()
        return custom_response("User deleted.", data=None, status_code=status.HTTP_204_NO_CONTENT, request=request)


# ---------------------------
# /api/auth/users/me/  -> get profile / update profile
# ---------------------------
class UserMeAPIView(APIView):
    """
    GET -> returns current authenticated user's profile
    PUT/PATCH -> update current user's profile
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current user's profile.",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return custom_response("Profile fetched.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)

    @swagger_auto_schema(
        operation_description="Update current user's profile.",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "Validation error"}
    )
    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response("Profile updated.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)

    @swagger_auto_schema(
        operation_description="Partially update current user's profile.",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "Validation error"}
    )
    def patch(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response("Profile partially updated.", data=serializer.data, status_code=status.HTTP_200_OK, request=request)


# ---------------------------
# /api/auth/switch-org/ -> switch current organization (requires auth)
# ---------------------------
class SwitchOrgAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Switch current organization (must be a member). Returns new tokens scoped to the org.",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'org_id': openapi.Schema(type=openapi.TYPE_INTEGER)
        }),
        responses={
            200: openapi.Response("Tokens", schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                'access': openapi.Schema(type=openapi.TYPE_STRING),
                'org_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'role': openapi.Schema(type=openapi.TYPE_STRING),
            })),
            400: "Bad request",
            403: "Not a member",
            500: "Tenants app not available"
        }
    )
    def post(self, request, *args, **kwargs):
        org_id_raw = request.data.get("org_id")
        if org_id_raw is None:
            return custom_response("org_id is required", status_code=status.HTTP_400_BAD_REQUEST, request=request, error="missing_org_id")

        # normalize org_id to int (handle string input)
        try:
            org_id = int(org_id_raw)
        except (ValueError, TypeError):
            return custom_response("org_id must be an integer", status_code=status.HTTP_400_BAD_REQUEST, request=request, error="invalid_org_id")

        try:
            from apps.tenants.models import OrganizationMembership
        except Exception:
            return custom_response("Tenants app is not available", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, request=request, error="tenants_missing")

        membership = OrganizationMembership.objects.filter(user=request.user, organization_id=org_id).first()
        if not membership:
            return custom_response("You are not a member of this organization.", status_code=status.HTTP_403_FORBIDDEN, request=request, error="not_member")

        refresh = RefreshToken.for_user(request.user)
        access = refresh.access_token
        access["org_id"] = org_id
        access["role"] = membership.role

        return custom_response("Organization switched.", data={
            "refresh": str(refresh),
            "access": str(access),
            "org_id": org_id,
            "role": membership.role,
        }, status_code=status.HTTP_200_OK, request=request)
