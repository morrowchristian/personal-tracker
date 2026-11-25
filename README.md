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
| `/api/me/` | GET | Current user's id, username, and email |
| `/api/tasks/` | GET, POST | List own tasks / create a task |
| `/api/tasks/<id>/` | GET, PATCH, DELETE | Retrieve / edit / delete own task |
| `/api/tasks/<id>/toggle/` | POST | Flip a task's completed flag |

All `/api/tasks/` endpoints require authentication and are scoped to the requesting user.

## Tests

Backend tests cover the Task API: create, list isolation, edit, toggle, delete, cross-user access (404), and unauthenticated rejection (401).

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
