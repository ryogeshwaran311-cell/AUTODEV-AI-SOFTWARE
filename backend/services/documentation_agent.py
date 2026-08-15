import os
import json
import logging
from typing import Dict, Any
from backend.services.gemini_service import gemini_service

logger = logging.getLogger("AutoDevAI.DocumentationAgent")

class DocumentationAgent:
    """
    Documentation Agent synthesizes comprehensive, production-grade README.md
    files reflecting the exact implemented features, architecture, and deployment procedures.
    """

    def generate_readme(self, project_path: str, requirements: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """Generates and writes README.md for the generated project."""
        project_name = requirements.get("project_name", "Full-Stack Application")
        slug = requirements.get("project_slug", "app")
        description = requirements.get("project_description", "Autonomous full-stack application.")
        features = requirements.get("features", [])
        models = plan.get("database_models", [])
        endpoints = plan.get("api_endpoints", [])

        logger.info(f"Documentation Agent writing README for: {project_name}")

        readme_content = f"""# {project_name}

> Generated autonomously by **AutoDevAI** – Multi-Agent Software Engineering System powered by Google Gemini.

## 📋 Project Overview

{description}

---

## ✨ Key Features

"""
        for f in features:
            title = f.get("title", "Feature")
            desc = f.get("description", "")
            readme_content += f"- **{title}**: {desc}\n"

        readme_content += f"""
---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, Lucide Icons, Pure Vanilla CSS (Glassmorphic dark design)
- **Backend**: Python 3.12+, Flask 3.0, Flask-CORS, Flask-SQLAlchemy
- **Database**: SQLite (Zero-configuration local persistence with SQLAlchemy ORM)
- **Deployment**: Vercel (Frontend Static SPA), Render (Backend Web Service)

---

## 📁 Project Architecture

```
{slug}/
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
.venv\\Scripts\\activate
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
"""

        for m in models:
            if m.get("class_name") == "User":
                continue
            tname = m.get("table_name", "items")
            cname = m.get("class_name", "Item")
            readme_content += f"| `GET` | `/api/{tname}` | Fetch all {tname} (supports `?search=` filter) |\n"
            readme_content += f"| `POST` | `/api/{tname}` | Create a new {cname} record |\n"
            readme_content += f"| `PUT` | `/api/{tname}/<id>` | Update an existing {cname} record |\n"
            readme_content += f"| `DELETE` | `/api/{tname}/<id>` | Remove a {cname} record |\n"

        readme_content += f"""
---

## 💾 Database Schema

The database is initialized automatically with SQLite upon startup (`db.create_all()`).

"""
        for m in models:
            cname = m.get("class_name")
            tname = m.get("table_name")
            cols = [f"`{c.get('name')}` ({c.get('type')})" for c in m.get("columns", [])]
            readme_content += f"- **{cname}** (`{tname}`): {', '.join(cols)}\n"

        readme_content += f"""
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
"""
        # Write file
        readme_file_path = os.path.join(project_path, "README.md")
        with open(readme_file_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(readme_content)

        return readme_content

documentation_agent = DocumentationAgent()
