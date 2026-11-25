# Personal Tracker

A full-stack personal task tracker: create, edit, complete, and delete your own tasks, with due dates and priorities. Each user only ever sees their own tasks.

Built with **React + Vite** on the frontend and **Django + Django REST Framework** on the backend, with JWT authentication.

## Live demo

Coming soon — deployment is in progress, and this section will link the live app once it's up.

## Features

- **Task CRUD** — create, list, edit, and delete tasks; each task has a title, optional description, due date, and priority (low / medium / high).
- **Toggle complete** — flip a task between active and completed with one click.
- **Filters** — view All, Active, or Completed tasks.
- **Per-user isolation** — tasks are scoped to the logged-in user at the API level. Another user's tasks are invisible: they don't appear in lists and can't be retrieved, edited, toggled, or deleted, even by direct id.
- **JWT authentication** — login with username and password; access and refresh tokens via SimpleJWT. Unauthenticated API requests are rejected with 401.
- **Sign in with GitHub (OAuth 2.0)** — one-click sign-in alongside the password login. The backend exchanges the GitHub code for a token, fetches the GitHub user, and links or creates the account (by GitHub user id, falling back to matching email); it then issues the same SimpleJWT tokens the password login uses. See "Sign in with GitHub" below for setup.
- **Dashboard UI** — add form, checkbox list, inline edit, delete with confirmation, empty states, and error handling.

## Tech stack

| Layer | Stack |
| --- | --- |
| Frontend | React 19, React Router 7, Axios, Vite 7 |
| Backend | Django 5.2, Django REST Framework 3.16, SimpleJWT 5.5 |
| Database | SQLite by default; PostgreSQL supported (`psycopg2-binary` is installed) |

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # accounts are created here (or in Django admin); there is no public signup
python manage.py runserver
```

The API runs at http://localhost:8000/api/.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at http://localhost:5173. It talks to the backend at `VITE_API_BASE_URL` (defaults to `http://localhost:8000/api`); set `VITE_API_BASE_URL` in a `.env` file to point at another backend.

## API

Base URL: `/api/`

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/ping/` | GET | Backend connectivity check |
| `/api/token/` | POST | Obtain JWT access + refresh tokens |
| `/api/token/refresh/` | POST | Refresh the access token |
| `/api/auth/github/` | GET | Start GitHub sign-in (returns the authorize URL + state) |
| `/api/auth/github/callback/` | POST | Exchange the GitHub code for JWT access + refresh tokens |
| `/api/me/` | GET | Current user's id, username, and email |
| `/api/tasks/` | GET, POST | List own tasks / create a task |
| `/api/tasks/<id>/` | GET, PATCH, DELETE | Retrieve / edit / delete own task |
| `/api/tasks/<id>/toggle/` | POST | Flip a task's completed flag |

All `/api/tasks/` endpoints require authentication and are scoped to the requesting user.

## Sign in with GitHub (OAuth 2.0)

The password login (`/api/token/`) keeps working untouched. GitHub sign-in is a second way in:

1. The login page's **Sign in with GitHub** button asks the backend for the GitHub authorize URL (`GET /api/auth/github/`), which returns the URL plus a random `state` token. The frontend stores the state and sends the browser to GitHub.
2. GitHub redirects back to the frontend callback page (`/auth/github/callback`) with a one-time code. The page checks the `state` matches, then POSTs the code to the backend (`POST /api/auth/github/callback/`).
3. The backend exchanges the code for a GitHub access token, fetches the GitHub user (and the verified email list if the user has no public email), then finds or creates the Django account: a returning GitHub user maps back to the same account via their GitHub id, and a GitHub login whose email matches an existing account is linked to it — never a duplicate. It then returns the same SimpleJWT access + refresh tokens the password login issues.

### Configuration

All OAuth config comes from environment variables — nothing is hardcoded:

| Variable | What it is |
| --- | --- |
| `GITHUB_CLIENT_ID` | Client ID of the GitHub OAuth app |
| `GITHUB_CLIENT_SECRET` | Client secret of the GitHub OAuth app |
| `GITHUB_OAUTH_CALLBACK_URL` | Full callback URL GitHub redirects to (defaults to `http://localhost:5173/auth/github/callback` for local dev) |

The callback URL format is `<frontend-origin>/auth/github/callback` — locally `http://localhost:5173/auth/github/callback`, in production the live frontend URL plus `/auth/github/callback`.

### Post-deploy setup (not done yet)

> The GitHub OAuth app does **not** exist yet, and the flow has **not** been tested against live GitHub. The code is complete and covered by mocked tests (see below); these steps run once the live demo exists:

1. Create the OAuth app at GitHub → Settings → Developer settings → OAuth Apps → New OAuth App. Set the **Authorization callback URL** to the live frontend URL plus `/auth/github/callback` (for example `https://<your-vercel-app>.vercel.app/auth/github/callback`). Homepage URL is the live frontend URL.
2. Copy the Client ID and generate a Client secret.
3. Set `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `GITHUB_OAUTH_CALLBACK_URL` (the full live callback URL from step 1) as environment variables on the backend host (Render).
4. Redeploy the backend. The frontend needs no extra env vars — it asks the backend for the authorize URL.
5. Test: click **Sign in with GitHub** on the live login page and confirm it lands on the dashboard.

Local dev works the same way with a second OAuth app (or the same one with the localhost callback added): set the three env vars before `python manage.py runserver`.

## Tests

Backend tests cover the Task API: create, list isolation, edit, toggle, delete, cross-user access (404), and unauthenticated rejection (401). They also cover GitHub sign-in with GitHub fully mocked (no real API calls): authorize URL, code exchange, new-user creation, returning-user reuse, email linking, no-public-email fallback, invalid codes, and missing config.

```bash
cd backend
python manage.py test core
```

## Project structure

```
personal-tracker/
├── backend/
│   ├── backend/        # Django project (settings, urls)
│   ├── core/           # Task model, serializer, views, urls, tests
│   └── manage.py
├── frontend/
│   └── src/
│       ├── api/        # Axios client + task/auth calls
│       ├── context/    # Auth provider
│       ├── pages/      # Dashboard, login
│       └── main.jsx
└── README.md
```

## License

This project is licensed under the MIT License.
