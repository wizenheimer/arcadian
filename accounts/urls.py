from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from accounts.views import (
    RegistrationView,
    LoginView,
    VerifyEmail,
    PasswordResetRequest,
    PasswordResetConfirm,
    AccountViewset,
    WorkspaceViewset,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"account",
    AccountViewset,
    basename="account",
)
router.register(
    r"workspace",
    WorkspaceViewset,
    basename="workspace",
)

urlpatterns = [
    path(
        "register/",
        RegistrationView.as_view(),
        name="register",
    ),
    path(
        "verify-email/",
        VerifyEmail.as_view(),
        name="verify-email",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "password-reset-request/",
        PasswordResetRequest.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirm.as_view(),
        name="password-reset-confirm",
    ),
    # The API URLs are now determined automatically by the router.
    path("", include(router.urls)),
]
