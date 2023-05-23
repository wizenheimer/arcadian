from rest_framework.views import APIView
from rest_framework.generics import (
    GenericAPIView,
)
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.encoding import (
    smart_str,
    smart_bytes,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    GeneratePasswordResetToken,
    AccountSerializer,
    WorkspaceSerializer,
)
from accounts.models import User, Workspace, WorkspaceAssignment
import accounts.invites as invite


class AccountViewset(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = AccountSerializer


class WorkspaceViewset(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer

    # TODO:
    # def get_queryset(self):
    #     user = self.request.user
    #     return user.workspace.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = self.request.user
        workspace = serializer.instance
        assignment = WorkspaceAssignment(workspace=workspace, user=user, is_admin=True)
        assignment.is_admin = True
        assignment.save()
        content = {
            "message": "created a new workspace",
            "pk": serializer.instance.pk,
        }
        return Response(
            content=content,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post", "get"])
    def invite(self, request, pk=None):
        if request.method == "POST":
            workspace = get_object_or_404(Workspace, pk=pk)
            user = request.user
            if not workspace.users.filter(id=user.id).exists():
                return Response(
                    {
                        "error": "You are not authorized to send invites for this workspace"
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            assignment = WorkspaceAssignment.objects.get(workspace=workspace, user=user)

            if not assignment.is_admin:
                return Response(
                    {
                        "error": "You are not authorized to send invites for this workspace"
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            email = self.request.data.get("email")
            if email is None:
                return Response(
                    {"error": "Email is required for generating an invite"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            User.objects.get_or_create(email=email)

            absurl = invite.get_invite_url(request, user.id, workspace.id, email)

            # Console Backend won't work without this.
            send_mail(
                subject="You've been invited to the workspace🥳",
                message=f"Get Started:{absurl}",
                from_email="djangomailer@mail.com",
                recipient_list=[
                    email,
                ],
            )

            return Response(
                {"message": "Invite shared successfully."}, status=status.HTTP_200_OK
            )
        else:
            workspace = self.request.query_params.get("workspace", None)
            sender = self.request.query_params.get("from", None)
            email = self.request.query_params.get("to", None)

            data = invite.decode_absurl(workspace, sender, email)

            workspace_id = data["workspace_id"]
            sender_id = data["sender_id"]
            email_id = data["email_id"]

            user = User.objects.get(email=email_id)
            workspace = Workspace.objects.get(id=workspace_id)

            assignment = WorkspaceAssignment(user=user, workspace=workspace)
            # TODO: set counterparty parameter during invite
            # TODO: prepare more roles for counterparty
            assignment.is_member = True
            assignment.save()

            return Response({"message": "Invited to the Workspace", "pk": workspace_id})

    @action(detail=True, methods=["post"])
    def assign_role(self, request, pk=None):
        workspace = get_object_or_404(Workspace, pk=pk)
        user = request.user
        assign_to = self.request.data.get("assign_to")
        assign_user = get_object_or_404(User, email=assign_to)
        assign_role = self.request.data.get("assign_role")
        remove_role = self.request.data.get("remove_role")

        roles = [
            "admin",
            "billing",
            "manager",
            "member",
            "counterparty",
        ]
        if assign_role and remove_role:
            return Response(
                {"error": "Grant parameters missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if assign_role not in roles:
            return Response(
                {"error": "Grant parameters missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not workspace.users.filter(id=user.id).exists():
            return Response(
                {"error": "You are not authorized to change roles for this workspace."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        assignment = WorkspaceAssignment.objects.get(workspace=workspace, user=user)

        if not assignment.is_admin:
            return Response(
                {"error": "You are not authorized to change roles for this workspace."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        assignment = WorkspaceAssignment.objects.get(
            workspace=workspace, user=assign_user
        )

        if assign_role == "admin":
            assignment.is_admin = True
        elif assign_role == "billing":
            assignment.is_billing = True
        elif assign_role == "manager":
            assignment.is_manager = True
        elif assign_role == "member":
            assignment.is_member = True
        elif assign_role == "counterparty":
            assignment.is_counterparty = True

        assignment.save()

        return Response(
            {"message": "Permission changed successfully."},
            status=status.HTTP_200_OK,
        )


class RegistrationView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = User.objects.get(email=user_data.get("email"))
        # token = RefreshToken.for_user(user)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user=user)

        current_site = get_current_site(request).domain
        relativeLink = reverse("verify-email")

        absurl = (
            "http://" + current_site + relativeLink + f"?token={token}&uidb64={uidb64}"
        )

        send_mail(
            subject="Verify email",
            message=f"Get Started:{absurl}",
            from_email="djangomailer@mail.com",
            recipient_list=[
                user.email,
            ],
        )

        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyEmail(APIView):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        uidb64 = request.GET.get("uidb64")
        uid = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, id=uid)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise ValidationError("Token is invalid.")
        user.is_verified = True
        user.is_active = True
        user.save()

        return Response(
            {"email": "email successfully activated."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirm(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        uidb64 = serializer.data.get("uidb64")
        password = serializer.data.get("password")

        uid = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        user.is_active = True
        user.set_password(password)
        user.save()

        return Response({"message": "Password changed successfully."})


class PasswordResetRequest(GenericAPIView):
    serializer_class = GeneratePasswordResetToken

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        print(email)
        user = User.objects.get(email=email)
        user.is_active = False
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user=user)

        current_site = get_current_site(request).domain
        relativeLink = reverse("password-reset-confirm")

        absurl = (
            "http://" + current_site + relativeLink + f"?uidb64={uidb64}&token={token}/"
        )

        send_mail(
            subject="Verify email",
            message=f"Link:{absurl}",
            from_email="djangomailer@mail.com",
            recipient_list=[
                user.email,
            ],
        )

        return Response({"message": "Password reset request sent successfully."})
