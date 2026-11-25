# backend/core/views.py
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .github_auth import (
    GitHubOAuthError,
    build_authorize_url,
    exchange_code_for_token,
    fetch_github_user,
    is_configured,
)
from .models import GitHubAccount, Task
from .serializers import TaskSerializer

User = get_user_model()


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })


class PingView(APIView):
    def get(self, request):
        return Response({"ping": "pong"})


def _get_or_create_user_for_github(github_user):
    """Find or create the Django user for a GitHub identity.

    Never creates a duplicate: a returning GitHub user maps back to the
    same account via GitHubAccount.github_id, and a GitHub login whose
    email matches an existing account is linked to that account.
    """
    try:
        account = GitHubAccount.objects.select_related("user").get(
            github_id=github_user["github_id"]
        )
        return account.user
    except GitHubAccount.DoesNotExist:
        pass

    email = github_user["email"]
    user = User.objects.filter(email=email).first() if email else None
    if user is None:
        username = github_user["login"]
        if User.objects.filter(username=username).exists():
            username = f"{username}-{github_user['github_id']}"
        # No password: this account signs in via GitHub only.
        user = User.objects.create_user(username=username, email=email)

    GitHubAccount.objects.create(
        user=user,
        github_id=github_user["github_id"],
        github_login=github_user["login"],
        avatar_url=github_user["avatar_url"],
    )
    return user


class GitHubLoginView(APIView):
    """Start Sign in with GitHub: return the GitHub authorize URL + state.

    The frontend stores the state (sessionStorage), redirects the browser
    to the URL, and checks the state on callback.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        if not is_configured():
            return Response(
                {"detail": "GitHub sign-in is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        authorize_url, state = build_authorize_url()
        return Response({"authorize_url": authorize_url, "state": state})


class GitHubCallbackView(APIView):
    """Finish Sign in with GitHub: exchange the code, return JWTs.

    POST {"code": "<one-time code from GitHub>"} ->
    {"access": "<jwt>", "refresh": "<jwt>"} for the linked/created user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        if not is_configured():
            return Response(
                {"detail": "GitHub sign-in is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        code = request.data.get("code")
        if not code:
            return Response(
                {"detail": "Missing authorization code."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = exchange_code_for_token(code)
            github_user = fetch_github_user(token)
        except GitHubOAuthError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        user = _get_or_create_user_for_github(github_user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {"access": str(refresh.access_token), "refresh": str(refresh)}
        )


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for the logged-in user's own tasks.

    The queryset is always scoped to request.user, so a user can
    never list, retrieve, update, or delete another user's tasks.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Flip a task's completed flag."""
        task = self.get_object()
        task.completed = not task.completed
        task.save(update_fields=["completed", "updated_at"])
        return Response(self.get_serializer(task).data)
