# backend/core/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DemoLoginView,
    GitHubCallbackView,
    GitHubLoginView,
    MeView,
    PingView,
    TaskViewSet,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/github/", GitHubLoginView.as_view(), name="github_login"),
    path(
        "auth/github/callback/",
        GitHubCallbackView.as_view(),
        name="github_callback",
    ),
    path("auth/demo/", DemoLoginView.as_view(), name="demo_login"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
