"""Tests for Sign in with GitHub (OAuth 2.0).

GitHub is fully mocked (``core.github_auth.urlopen`` is patched) — no test
ever hits the real GitHub API. Covers: authorize URL, code exchange,
find-or-create/link, no duplicates, invalid codes, and missing config.
"""

import io
import json
import urllib.error
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import GitHubAccount

User = get_user_model()

OAUTH_SETTINGS = {
    "GITHUB_CLIENT_ID": "test-client-id",
    "GITHUB_CLIENT_SECRET": "test-client-secret",
    "GITHUB_OAUTH_CALLBACK_URL": "http://localhost:5173/auth/github/callback",
}

USER_PAYLOAD = {
    "id": 12345,
    "login": "octocat",
    "email": "octo@example.com",
    "avatar_url": "https://example.com/avatar.png",
}


class FakeResponse:
    """Minimal urlopen stand-in: a context manager returning JSON bytes."""

    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def make_fake_urlopen(
    user_payload=None,
    emails_payload=None,
    token_error=False,
):
    """Build a fake urlopen that answers like GitHub would."""

    def fake_urlopen(request, timeout=10):
        url = request.full_url
        if "login/oauth/access_token" in url:
            if token_error:
                raise urllib.error.HTTPError(
                    url,
                    400,
                    "Bad Request",
                    {},
                    io.BytesIO(
                        b'{"error": "bad_verification_code", '
                        b'"error_description": "The code passed is incorrect or expired."}'
                    ),
                )
            return FakeResponse({"access_token": "gh_test_token"})
        if url.endswith("/user/emails"):
            return FakeResponse(
                emails_payload
                if emails_payload is not None
                else [
                    {
                        "email": "octo-private@example.com",
                        "primary": True,
                        "verified": True,
                    }
                ]
            )
        if url.endswith("/user"):
            return FakeResponse(
                user_payload if user_payload is not None else USER_PAYLOAD
            )
        raise AssertionError(f"Unexpected GitHub URL in test: {url}")

    return fake_urlopen


@override_settings(**OAUTH_SETTINGS)
class GitHubOAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_returns_authorize_url(self):
        """GET /api/auth/github/ returns the GitHub authorize URL + state."""
        response = self.client.get("/api/auth/github/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = response.data["authorize_url"]
        self.assertIn("https://github.com/login/oauth/authorize", url)
        self.assertIn("client_id=test-client-id", url)
        self.assertIn(
            "redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fauth%2Fgithub%2Fcallback",
            url,
        )
        self.assertIn("scope=user%3Aemail", url)
        self.assertTrue(response.data["state"])

    def test_callback_creates_new_user_and_returns_jwts(self):
        """A valid code creates a user + GitHubAccount and returns JWTs."""
        with patch(
            "core.github_auth.urlopen", make_fake_urlopen()
        ):
            response = self.client.post(
                "/api/auth/github/callback/",
                {"code": "valid-code"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        user = User.objects.get(username="octocat")
        self.assertEqual(user.email, "octo@example.com")
        account = GitHubAccount.objects.get(github_id=12345)
        self.assertEqual(account.user, user)
        self.assertEqual(account.github_login, "octocat")

        # The issued access token actually authenticates as that user.
        authed = APIClient()
        authed.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        me = authed.get("/api/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], "octocat")

    def test_callback_returning_user_reuses_account(self):
        """A returning GitHub user gets the same account — no duplicates."""
        with patch(
            "core.github_auth.urlopen", make_fake_urlopen()
        ):
            first = self.client.post(
                "/api/auth/github/callback/", {"code": "code-one"}, format="json"
            )
            second = self.client.post(
                "/api/auth/github/callback/", {"code": "code-two"}, format="json"
            )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(GitHubAccount.objects.count(), 1)
        self.assertEqual(
            User.objects.get(username="octocat").pk,
            GitHubAccount.objects.get(github_id=12345).user_id,
        )

    def test_callback_invalid_code_returns_400_and_creates_nothing(self):
        """An invalid/expired code is rejected and creates nothing."""
        with patch(
            "core.github_auth.urlopen", make_fake_urlopen(token_error=True)
        ):
            response = self.client.post(
                "/api/auth/github/callback/",
                {"code": "bad-code"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(GitHubAccount.objects.count(), 0)

    def test_callback_missing_code_returns_400(self):
        """A callback with no code is rejected."""
        response = self.client.post(
            "/api/auth/github/callback/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_callback_no_public_email_uses_emails_endpoint(self):
        """A GitHub user with no public email falls back to /user/emails."""
        user_payload = dict(USER_PAYLOAD, email=None)
        with patch(
            "core.github_auth.urlopen",
            make_fake_urlopen(user_payload=user_payload),
        ):
            response = self.client.post(
                "/api/auth/github/callback/",
                {"code": "valid-code"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(username="octocat")
        self.assertEqual(user.email, "octo-private@example.com")

    def test_callback_without_any_email_still_works(self):
        """A GitHub user with no verified email at all still gets an account."""
        user_payload = dict(USER_PAYLOAD, email=None)
        with patch(
            "core.github_auth.urlopen",
            make_fake_urlopen(user_payload=user_payload, emails_payload=[]),
        ):
            response = self.client.post(
                "/api/auth/github/callback/",
                {"code": "valid-code"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(username="octocat")
        self.assertEqual(user.email, "")

    def test_callback_links_existing_user_by_email(self):
        """A GitHub login whose email matches an account links to it."""
        existing = User.objects.create_user(
            username="octo-admin",
            email="octo@example.com",
            password="password123",
        )
        with patch(
            "core.github_auth.urlopen", make_fake_urlopen()
        ):
            response = self.client.post(
                "/api/auth/github/callback/",
                {"code": "valid-code"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        account = GitHubAccount.objects.get(github_id=12345)
        self.assertEqual(account.user, existing)


@override_settings(
    GITHUB_CLIENT_ID="",
    GITHUB_CLIENT_SECRET="",
    GITHUB_OAUTH_CALLBACK_URL="http://localhost:5173/auth/github/callback",
)
class GitHubOAuthUnconfiguredTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_unconfigured_returns_503(self):
        """Without OAuth credentials, the login endpoint says so."""
        response = self.client.get("/api/auth/github/")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_callback_unconfigured_returns_503(self):
        """Without OAuth credentials, the callback refuses the code."""
        response = self.client.post(
            "/api/auth/github/callback/", {"code": "any-code"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(User.objects.count(), 0)
