# Personal Tracker

Personal Tracker is a full-stack web application designed to help users manage and track personal tasks and projects. Built with **React** on the frontend and **Django + DRF** on the backend, this project provides a clean, modular, and secure system for task management with authentication and real-time data updates.

---

## Table of Contents
- [Features](#features)
- [Upcoming Features](#upcoming-features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Authentication & User Management
- **Secure Login/Logout** with JWT authentication.
- **User Profiles**: View user details such as username, email, and ID.
- **Protected Routes**: Access to dashboard and user-specific content is restricted to authenticated users only.

### Dashboard & Task Management
- **Real-Time API Ping**: Checks backend connectivity.
- **Task CRUD**: Create, list, edit, complete, and delete your own tasks, with due dates and priorities — each user only sees their own tasks.
- **Task Filters**: View all, active, or completed tasks.
- **Logout Functionality**: Quickly end session from dashboard.

### Frontend UI
- **Responsive Design**: Clean and mobile-friendly UI.
- **Form Handling**: Robust login form with error handling.
- **Component-Based Architecture**: Modular React components for scalable UI development.

### Backend API
- **RESTful Endpoints**: Structured API for easy integration with frontend.
- **Modular App Structure**: Core app with expandable API endpoints for tasks, users, and projects.
- **DRF Permissions**: Built-in authentication and permission handling with Django REST Framework.

---

## Upcoming Features

### Development & Deployment
- **Docker Support**: Containerization for backend and frontend, enabling seamless deployment.
- **DevContainers**: VS Code DevContainers for consistent development environments across contributors.
- **CI/CD Pipelines**: Automated testing, linting, and deployment for production-ready apps.

### Backend Enhancements
- **Expanded API**: New endpoints for projects and activity logs.
- **Role-Based Access Control**: Assign roles and permissions to different users.
- **JWT Refresh & OAuth**: Improved authentication workflows, including token refresh and third-party OAuth login options.
- **Logging & Error Tracking**: Integrated backend monitoring tools for easier debugging.

### Frontend Enhancements
- **Dashboard Components**: New components like tables, cards, charts for data visualization.
- **Dark Mode / Theme Switching**: User-selectable light/dark modes.
- **Enhanced Error Handling**: Visual feedback for API failures and loading states.
- **Notifications**: Push notifications for task updates and reminders.

### Analytics & Monitoring
- **Performance Metrics**: Dashboard for tracking app performance and user engagement.
- **Activity Logs**: Track user actions for better insights and auditing.

### Future Integrations
- **Third-Party API Integrations**: For project management, calendar sync, or cloud storage.
- **Mobile-Friendly Optimizations**: Ready for eventual React Native or PWA support.

---

## Tech Stack

**Frontend**: React, React Router, Context API, Axios  
**Backend**: Django, Django REST Framework  
**Authentication**: JWT (JSON Web Tokens)  
**Database**: SQLite (default) / PostgreSQL (optional)  
**Dev Tools**: VS Code, Git, Vite  

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm / pnpm
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install   # or pnpm install
npm run dev   # start development server
```
Visit http://localhost:5173 for the frontend and http://localhost:8000/api/ for the backend API.

## Project Structure
```bash
personal-tracker/
├─ backend/
│  ├─ core/
│  │  ├─ views.py
│  │  ├─ urls.py
│  └─ manage.py
├─ frontend/
│  ├─ src/
│  │  ├─ pages/
│  │  ├─ components/
│  │  └─ App.jsx
├─ .gitignore
├─ README.md
└─ requirements.txt
```

## Contributing
1. Fork the repository.
2. Create a feature branch: git checkout -b feature/your-feature
3. Commit your changes: git commit -m "Add feature"
4. Push to branch: git push origin feature/your-feature
5. Open a pull request.

## License
This project is licened under the MIT License.