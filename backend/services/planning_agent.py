import logging
from typing import Dict, Any
from backend.services.gemini_service import gemini_service

logger = logging.getLogger("AutoDevAI.PlanningAgent")

class PlanningAgent:
    """
    Planning Agent designs the detailed architecture blueprint: database schemas,
    API endpoint specs, frontend component architecture, and dependencies.
    """

    SYSTEM_INSTRUCTION = """
You are the Principal Software Architect in the AutoDevAI Autonomous Multi-Agent Engineering Team.
Your job is to receive structured requirements and generate a rigorous, fully specified implementation architecture plan in strict JSON.

Do NOT generate raw code yet. Design:
1. "project_summary": High-level architecture summary
2. "database_models": Array of model specifications:
   [
     {
       "table_name": "students",
       "class_name": "Student",
       "columns": [
         {"name": "id", "type": "Integer", "primary_key": true},
         {"name": "first_name", "type": "String(100)", "nullable": false},
         {"name": "email", "type": "String(120)", "unique": true, "nullable": false},
         {"name": "created_at", "type": "DateTime", "default": "datetime.utcnow"}
       ],
       "relationships": []
     }
   ]
3. "api_endpoints": Array of endpoint specifications:
   [
     {
       "path": "/api/students",
       "method": "GET",
       "description": "List students with search & filter query params",
       "request_params": ["search", "grade"],
       "response_sample": {"students": [], "total": 0}
     }
   ]
4. "frontend_pages": Array of pages with components used:
   [
     {"page_name": "Dashboard", "description": "Overview metrics and recent activities", "components": ["StatsCards", "RecentActivityTable"]}
   ]
5. "frontend_components": Array of reusable component names and their responsibilities
6. "python_dependencies": ["flask>=3.0.0", "flask-cors>=4.0.0", "flask-sqlalchemy>=3.1.1", "python-dotenv>=1.0.0"]
7. "npm_dependencies": {
     "dependencies": {"react": "^18.3.1", "react-dom": "^18.3.1", "lucide-react": "^0.344.0"},
     "devDependencies": {"@vitejs/plugin-react": "^4.3.1", "vite": "^5.4.0"}
   }
8. "testing_plan": Array of validation checks to run
9. "deployment_plan": {"frontend": "Vercel", "backend": "Render"}

Return STRICT JSON only.
"""

    def plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Creates complete technical architecture plan from requirements."""
        logger.info(f"Planning Agent designing architecture for: '{requirements.get('project_name')}'")

        if gemini_service.is_configured():
            try:
                user_msg = f"Requirements Specification:\n{json.dumps(requirements, indent=2)}\n\nGenerate complete technical plan JSON."
                result = gemini_service.generate_json(
                    prompt=user_msg,
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=0.2
                )
                if "database_models" in result and "api_endpoints" in result:
                    return result
            except Exception as e:
                logger.warning(f"Planning Agent Gemini call failed: {e}. Falling back to heuristic plan.")

        return self._heuristic_plan(requirements)

    def _heuristic_plan(self, reqs: Dict[str, Any]) -> Dict[str, Any]:
        """Heuristic architectural plan matching the requirements."""
        project_name = reqs.get("project_name", "Application")
        slug = reqs.get("project_slug", "app")
        entities = reqs.get("database_entities", [])

        # Build database models
        models = []
        # Always include User model if not present
        has_user = any(e.get("entity", "").lower() == "user" for e in entities)
        if not has_user:
            models.append({
                "table_name": "users",
                "class_name": "User",
                "columns": [
                    {"name": "id", "type": "Integer", "primary_key": True},
                    {"name": "username", "type": "String(80)", "unique": True, "nullable": False},
                    {"name": "email", "type": "String(120)", "unique": True, "nullable": False},
                    {"name": "password_hash", "type": "String(200)", "nullable": False, "default": "admin123"},
                    {"name": "role", "type": "String(50)", "default": "Admin"},
                    {"name": "created_at", "type": "DateTime", "default": "datetime.utcnow"}
                ]
            })

        for e in entities:
            entity_name = e.get("entity", "Item")
            class_name = entity_name.capitalize()
            table_name = entity_name.lower() + ("s" if not entity_name.endswith("s") else "")
            fields = e.get("fields", ["id", "name", "created_at"])

            cols = []
            for f in fields:
                if f == "id":
                    cols.append({"name": "id", "type": "Integer", "primary_key": True})
                elif "date" in f or "time" in f or f.endswith("_at"):
                    cols.append({"name": f, "type": "DateTime", "default": "datetime.utcnow"})
                elif f in ["price", "amount", "credits", "salary", "rating"]:
                    cols.append({"name": f, "type": "Float", "default": 0.0})
                elif f in ["stock", "quantity", "roll_no", "age", "student_id", "user_id", "project_id"]:
                    cols.append({"name": f, "type": "Integer", "default": 1})
                elif f in ["is_active", "status_bool", "completed", "present"]:
                    cols.append({"name": f, "type": "Boolean", "default": True})
                elif f in ["description", "remarks", "address", "notes", "content"]:
                    cols.append({"name": f, "type": "Text", "nullable": True})
                else:
                    cols.append({"name": f, "type": "String(200)", "nullable": False if f in ["name", "title", "email", "username"] else True})

            models.append({
                "table_name": table_name,
                "class_name": class_name,
                "columns": cols
            })

        # Build API endpoints
        endpoints = [
            {"path": "/api/health", "method": "GET", "description": "Backend health and status probe", "response_sample": {"status": "ok", "app": project_name}},
            {"path": "/api/auth/login", "method": "POST", "description": "User login and session creation", "request_body": {"username": "admin", "password": "password"}, "response_sample": {"success": True, "user": {"username": "admin", "role": "Admin"}}},
            {"path": "/api/stats", "method": "GET", "description": "Summary KPI statistics for the dashboard", "response_sample": {"total_items": 42, "recent_count": 12, "active_status": "Healthy"}}
        ]

        for m in models:
            if m["class_name"] == "User":
                continue
            base = f"/api/{m['table_name']}"
            endpoints.extend([
                {"path": base, "method": "GET", "description": f"Fetch all {m['table_name']} with optional search & filter", "request_params": ["q", "limit"], "response_sample": {m['table_name']: []}},
                {"path": base, "method": "POST", "description": f"Create a new {m['class_name']}", "request_body": {c['name']: "sample" for c in m['columns'] if not c.get('primary_key')}},
                {"path": f"{base}/<int:id>", "method": "GET", "description": f"Get {m['class_name']} by ID"},
                {"path": f"{base}/<int:id>", "method": "PUT", "description": f"Update {m['class_name']} by ID"},
                {"path": f"{base}/<int:id>", "method": "DELETE", "description": f"Delete {m['class_name']} by ID"}
            ])

        return {
            "project_summary": f"Full-stack architecture for {project_name} utilizing Flask REST API, SQLite database with SQLAlchemy ORM, and React + Vite modern dashboard UI.",
            "database_models": models,
            "api_endpoints": endpoints,
            "frontend_pages": [
                {"page_name": "Dashboard", "description": "KPI counters, overview charts, quick actions", "components": ["StatsCards", "QuickCreateModal", "RecentActivity"]},
                {"page_name": "ManageRecords", "description": "Complete data management table with search, filter, edit, delete", "components": ["DataTable", "RecordModal", "SearchBar", "Pagination"]},
                {"page_name": "Analytics", "description": "Statistical breakdowns and reporting", "components": ["MetricCards", "DistributionView"]},
                {"page_name": "Settings", "description": "System preferences and demo configuration", "components": ["SystemInfoCard", "ResetDatabaseModal"]}
            ],
            "frontend_components": [
                "Navbar", "Sidebar", "StatsCard", "DataTable", "ModalForm", "ToastNotification", "ConfirmDialog", "SearchBar", "StatusBadge"
            ],
            "python_dependencies": [
                "flask>=3.0.0",
                "flask-cors>=4.0.0",
                "flask-sqlalchemy>=3.1.1",
                "python-dotenv>=1.0.0"
            ],
            "npm_dependencies": {
                "dependencies": {
                    "react": "^18.3.1",
                    "react-dom": "^18.3.1",
                    "lucide-react": "^0.344.0"
                },
                "devDependencies": {
                    "@vitejs/plugin-react": "^4.3.1",
                    "vite": "^5.4.0"
                }
            },
            "testing_plan": [
                "Verify all required project directories and files are present",
                "Validate Python syntax and SQLAlchemy database schema compilation",
                "Initialize SQLite database tables with db.create_all()",
                "Check package.json dependencies against frontend imports",
                "Execute syntax and lint checks on React JSX files",
                "Verify CORS configuration and backend API routes"
            ],
            "deployment_plan": {
                "frontend": "Vercel (Static SPA build via vite build)",
                "backend": "Render (Python web service with gunicorn/python app.py)"
            }
        }

planning_agent = PlanningAgent()
