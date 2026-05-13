# 🚀 TaskFlow | Advanced Team Task Manager

TaskFlow is a robust, full-stack project management application designed for teams. It combines a powerful **Django REST Framework** backend with a premium, responsive **Vanilla JavaScript/CSS** frontend. 

![TaskFlow Interface](https://img.shields.io/badge/UI-Glassmorphism-blueviolet?style=for-the-badge)
![Django](https://img.shields.io/badge/Backend-Django_6.0-green?style=for-the-badge&logo=django)
![JWT](https://img.shields.io/badge/Auth-JWT_Secure-orange?style=for-the-badge)

---

## ✨ Key Features

### 🔐 Security & Identity
- **JWT Authentication**: Stateless, secure login using JSON Web Tokens.
- **Role-Based Access Control (RBAC)**: Distinct permissions for **Admins** (Creators) and **Members** (Contributors).
- **Change Password**: Secure in-app password updates verifying the current credentials.

### 📊 Project Management
- **Team Collaboration**: Admins can create projects and assign multiple team members.
- **Scoped Visibility**: Users only see projects they are members of.
- **Deadline Tracking**: Real-time monitoring of project completion dates.

### 📝 Task Tracking
- **Granular Assignments**: Assign specific tasks to individual team members.
- **Priority System**: Categorize tasks by `Low`, `Medium`, or `High` priority.
- **Interactive Status**: Seamlessly update tasks from `Pending` → `In Progress` → `Completed`.

### 🎨 Premium UI/UX
- **Single Page Application (SPA)**: Ultra-fast view transitions without page reloads.
- **Glassmorphism Design**: Modern dark-themed interface with blurred effects and smooth animations.
- **Real-time Feedback**: Animated toast notifications and loading progress bars for all interactions.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Django 6.0, Django REST Framework, SimpleJWT.
- **Frontend**: HTML5, Vanilla CSS3 (Custom Properties), ES6+ JavaScript.
- **Database**: PostgreSQL (Production ready), SQLite (Testing).
- **Testing**: Pytest & Pytest-Django.
- **DevOps**: GitHub Actions (CI/CD).


