# Calci

> Generated autonomously by **AutoDevAI** – Multi-Agent Software Engineering System powered by Google Gemini.

## 📋 Project Overview

A full-stack, responsive web application for calci featuring real-time dashboard analytics, complete CRUD workflows, search and filtering, and SQLite database persistence.

---

## ✨ Key Features

- **Authentication & Role Access**: Admin login, session authorization, and permission control.
- **Comprehensive CRUD Management**: Create, read, update, search, and delete domain records with instant form validation.
- **Dashboard Metrics & Statistics**: Overview KPIs, status distribution cards, and real-time summary statistics.
- **Fast Search and Filter**: Client & server side search by keywords, categories, and date ranges.
- **Data Export and Activity History**: Track history logs and quick status transitions.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, Lucide Icons, Pure Vanilla CSS (Glassmorphic dark design)
- **Backend**: Python 3.12+, Flask 3.0, Flask-CORS, Flask-SQLAlchemy
- **Database**: SQLite (Zero-configuration local persistence with SQLAlchemy ORM)
- **Deployment**: Vercel (Frontend Static SPA), Render (Backend Web Service)

---

## 📁 Project Architecture

```
calci/
├── backend/
│   ├── app.py              # Flask server, CORS & REST API routes
│   ├── database.py         # SQLAlchemy instance
│   ├── models.py           # SQLite database schema models
│   ├── requirements.txt    # Python backend dependencies
│   └── services/           # Helper domain services
│
├── frontend/
│   ├── public/             # Static web assets
│   ├── src/
│   │   ├── main.jsx        # React entrypoint
│   │   ├── App.jsx         # Main application container with CRUD state
│   │   ├── index.css       # Design tokens & responsive styles
│   │   └── components/     # Reusable UI components
│   │       ├── Navbar.jsx
│   │       ├── Sidebar.jsx
│   │       ├── StatsCard.jsx
│   │       ├── DataTable.jsx
│   │       └── ModalForm.jsx
│   ├── index.html          # HTML5 shell
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite dev server & API proxy
│
├── vercel.json             # Vercel deployment specification
├── render.yaml             # Render deployment specification
└── README.md               # Project documentation
```

---

## 🚀 Quick Start (Local Setup)

### 1. Start the Backend Server

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```
Backend will start on `http://localhost:5000` (or configured port).

### 2. Start the Frontend Application

```bash
cd frontend
npm install
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check & service status |
| `GET` | `/api/stats` | Summary KPI metrics for dashboard |
| `POST` | `/api/auth/login` | Authentication demo login |
| `GET` | `/api/items` | Fetch all items (supports `?search=` filter) |
| `POST` | `/api/items` | Create a new Item record |
| `PUT` | `/api/items/<id>` | Update an existing Item record |
| `DELETE` | `/api/items/<id>` | Remove a Item record |
| `GET` | `/api/logs` | Fetch all logs (supports `?search=` filter) |
| `POST` | `/api/logs` | Create a new Log record |
| `PUT` | `/api/logs/<id>` | Update an existing Log record |
| `DELETE` | `/api/logs/<id>` | Remove a Log record |

---

## 💾 Database Schema

The database is initialized automatically with SQLite upon startup (`db.create_all()`).

- **User** (`users`): `id` (Integer), `username` (String(200)), `email` (String(200)), `role` (String(200)), `created_at` (DateTime)
- **Item** (`items`): `id` (Integer), `title` (String(200)), `description` (Text), `category` (String(200)), `status` (String(200)), `created_at` (DateTime), `updated_at` (DateTime)
- **Log** (`logs`): `id` (Integer), `item_id` (String(200)), `action` (String(200)), `timestamp` (DateTime), `performed_by` (String(200))

---

## 🌐 Deployment Guide

### Deploy Frontend to Vercel
1. Import the repository into [Vercel](https://vercel.com).
2. Set Root Directory to `frontend`.
3. Build command: `npm run build`, Output directory: `dist`.

### Deploy Backend to Render
1. Create a new Web Service on [Render](https://render.com).
2. Connect repository and use `render.yaml` or set:
   - Environment: `Python`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python backend/app.py`

---

*Generated autonomously with ❤️ by AutoDevAI.*
