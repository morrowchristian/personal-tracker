"""GitHub OAuth 2.0 helpers (manual code exchange, stdlib only).

Flow: the frontend redirects the user to GitHub's authorize URL; GitHub
redirects back to the frontend callback with a one-time code; the frontend
POSTs that code to the backend, which exchanges it for a GitHub access
token, fetches the GitHub user, and the view issues our own JWTs.

No new dependencies: all HTTP goes through urllib. ``urlopen`` is imported
into this module so tests can patch ``core.github_auth.urlopen``.
"""

import json
import secrets
import urllib.error
import urllib.parse
from urllib.request import Request, urlopen

from django.conf import settings

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_USER_EMAILS_URL = "https://api.github.com/user/emails"


class GitHubOAuthError(Exception):
    """Raised when any step of the GitHub OAuth flow fails."""


def is_configured():
    """True once the OAuth app credentials are set in the environment."""
    return bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)


def build_authorize_url():
    """Return (authorize_url, state) for the GitHub authorize step.

    The state is a random token the frontend stores (sessionStorage) and
    checks on callback, so a forged callback cannot be replayed.
    """
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_OAUTH_CALLBACK_URL,
        "scope": "user:email",
        "state": state,
    }
    return f"{GITHUB_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}", state


def _post_json(url, data, headers=None):
    body = urllib.parse.urlencode(data).encode()
    req = Request(url, data=body, headers=headers or {}, method="POST")
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise GitHubOAuthError(f"GitHub request failed ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise GitHubOAuthError(f"Could not reach GitHub: {exc.reason}") from exc


def _get_json(url, token):
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "personal-tracker",
        },
    )
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise GitHubOAuthError(f"GitHub request failed ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise GitHubOAuthError(f"Could not reach GitHub: {exc.reason}") from exc


def exchange_code_for_token(code):
    """Exchange a one-time authorization code for a GitHub access token."""
    data = _post_json(
        GITHUB_TOKEN_URL,
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_OAUTH_CALLBACK_URL,
        },
        headers={"Accept": "application/json"},
    )
    if "error" in data:
        raise GitHubOAuthError(data.get("error_description") or data["error"])
    token = data.get("access_token")
    if not token:
        raise GitHubOAuthError("GitHub did not return an access token")
    return token


def fetch_github_user(token):
    """Fetch the GitHub user for a token.

    Returns {"github_id", "login", "email", "avatar_url"}. A GitHub user
    with no public email is handled by asking for the verified email list;
    if there is no verified email at all, email is "" (the account still
    works — email is not required to sign in).
    """
    user = _get_json(GITHUB_USER_URL, token)
    if not user.get("id") or not user.get("login"):
        raise GitHubOAuthError("GitHub did not return a user id/login")

    email = user.get("email")
    if not email:
        emails = _get_json(GITHUB_USER_EMAILS_URL, token)
        primary = next(
            (e for e in emails if e.get("primary") and e.get("verified")), None
        )
        chosen = primary or next(
            (e for e in emails if e.get("verified")), None
        )
        email = (chosen or {}).get("email")

    return {
        "github_id": user["id"],
        "login": user["login"],
        "email": email or "",
        "avatar_url": user.get("avatar_url") or "",
    }
