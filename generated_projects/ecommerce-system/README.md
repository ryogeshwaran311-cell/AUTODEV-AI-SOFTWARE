# E-Commerce Management System

> Generated autonomously by **AutoDevAI** – Multi-Agent Software Engineering System powered by Google Gemini.

## 📋 Project Overview

A full-stack, responsive web application for e-commerce management system featuring real-time dashboard analytics, complete CRUD workflows, search and filtering, and SQLite database persistence.

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
ecommerce-system/
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
| `GET` | `/api/products` | Fetch all products (supports `?search=` filter) |
| `POST` | `/api/products` | Create a new Product record |
| `PUT` | `/api/products/<id>` | Update an existing Product record |
| `DELETE` | `/api/products/<id>` | Remove a Product record |
| `GET` | `/api/orders` | Fetch all orders (supports `?search=` filter) |
| `POST` | `/api/orders` | Create a new Order record |
| `PUT` | `/api/orders/<id>` | Update an existing Order record |
| `DELETE` | `/api/orders/<id>` | Remove a Order record |
| `GET` | `/api/orderitems` | Fetch all orderitems (supports `?search=` filter) |
| `POST` | `/api/orderitems` | Create a new Orderitem record |
| `PUT` | `/api/orderitems/<id>` | Update an existing Orderitem record |
| `DELETE` | `/api/orderitems/<id>` | Remove a Orderitem record |

---

## 💾 Database Schema

The database is initialized automatically with SQLite upon startup (`db.create_all()`).

- **User** (`users`): `id` (Integer), `username` (String(200)), `email` (String(200)), `role` (String(200)), `created_at` (DateTime)
- **Product** (`products`): `id` (Integer), `name` (String(200)), `category` (String(200)), `price` (Float), `stock` (Integer), `description` (Text), `image_url` (String(200))
- **Order** (`orders`): `id` (Integer), `user_id` (Integer), `total_amount` (String(200)), `status` (String(200)), `created_at` (DateTime)
- **Orderitem** (`orderitems`): `id` (Integer), `order_id` (String(200)), `product_id` (String(200)), `quantity` (Integer), `unit_price` (String(200))

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
