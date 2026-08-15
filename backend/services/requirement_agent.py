import re
import json
import logging
from typing import Dict, Any
from backend.services.gemini_service import gemini_service

logger = logging.getLogger("AutoDevAI.RequirementAgent")

class RequirementAgent:
    """
    Requirement Agent converts raw natural-language software ideas into structured,
    machine-readable specifications with user roles, features, pages, APIs, and DB entities.
    """

    SYSTEM_INSTRUCTION = """
You are the Lead Requirement Analyst in the AutoDevAI Autonomous Multi-Agent Engineering Team.
Your job is to analyze the user's software idea and extract a complete, formal, structured specification in strict JSON.

Do NOT generate code. Extract:
1. "project_name": Professional Title (e.g. "Student Management System")
2. "project_slug": Lowercase alphanumeric slug with hyphens (e.g. "student-management-system")
3. "project_description": Clear 2-3 sentence overview of the application purpose and workflow
4. "target_users": Array of target user personas
5. "user_roles": Array of system roles (e.g. ["Admin", "Student", "Teacher"] or ["Admin", "User"])
6. "features": Array of objects: [{"id": "feat_1", "title": "...", "description": "...", "priority": "high/medium"}]
7. "pages": Array of UI views (e.g. ["Dashboard", "StudentsList", "AttendanceTracker", "Login", "Reports"])
8. "components": Array of reusable frontend components needed
9. "api_requirements": Array of objects: [{"endpoint": "/api/...", "method": "GET/POST/PUT/DELETE", "purpose": "..."}]
10. "database_entities": Array of objects: [{"entity": "Student", "fields": ["id", "name", "email", "roll_number", "created_at"]}]
11. "authentication_requirements": Object describing login/token requirements
12. "validation_requirements": Array of validation rules (e.g. "Email format validation", "Unique roll number")
13. "non_functional_requirements": Array of standards (e.g. "SQLite local persistence", "CORS enabled", "Responsive CSS", "Zero-dependency frontend")

Return STRICT JSON only.
"""

    def analyze(self, user_prompt: str) -> Dict[str, Any]:
        """Analyzes prompt and returns structured requirements specification."""
        logger.info(f"Requirement Agent analyzing prompt: '{user_prompt[:80]}...'")

        if gemini_service.is_configured():
            try:
                user_msg = f"User Software Idea:\n{user_prompt}\n\nGenerate full structured requirements JSON."
                result = gemini_service.generate_json(
                    prompt=user_msg,
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=0.2
                )
                if "project_name" in result and "features" in result:
                    # Sanitize slug
                    if "project_slug" not in result or not result["project_slug"]:
                        result["project_slug"] = self._generate_slug(result.get("project_name", "app"))
                    return result
            except Exception as e:
                logger.warning(f"Requirement Agent Gemini call failed: {e}. Falling back to heuristic analyzer.")

        return self._heuristic_requirements(user_prompt)

    def _generate_slug(self, name: str) -> str:
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug or "custom-app"

    def _heuristic_requirements(self, prompt: str) -> Dict[str, Any]:
        """Provides rich structured fallback requirement specification."""
        p_lower = prompt.lower()
        
        # Determine title
        if "student" in p_lower:
            project_name = "Student Management System"
            slug = "student-management-system"
            entities = [
                {"entity": "User", "fields": ["id", "username", "email", "role", "password_hash", "created_at"]},
                {"entity": "Student", "fields": ["id", "first_name", "last_name", "email", "roll_no", "grade", "phone", "address", "enrollment_date"]},
                {"entity": "Attendance", "fields": ["id", "student_id", "date", "status", "remarks"]},
                {"entity": "Course", "fields": ["id", "course_code", "course_name", "instructor", "credits"]}
            ]
            pages = ["Dashboard", "Students", "Attendance", "Courses", "Login", "Reports"]
            roles = ["Admin", "Teacher", "Student"]
        elif "shop" in p_lower or "commerce" in p_lower or "store" in p_lower:
            project_name = "E-Commerce Management System"
            slug = "ecommerce-system"
            entities = [
                {"entity": "User", "fields": ["id", "username", "email", "role", "created_at"]},
                {"entity": "Product", "fields": ["id", "name", "category", "price", "stock", "description", "image_url"]},
                {"entity": "Order", "fields": ["id", "user_id", "total_amount", "status", "created_at"]},
                {"entity": "OrderItem", "fields": ["id", "order_id", "product_id", "quantity", "unit_price"]}
            ]
            pages = ["Dashboard", "Products", "Orders", "Customers", "Analytics", "Login"]
            roles = ["Admin", "Manager", "Customer"]
        elif "task" in p_lower or "kanban" in p_lower or "todo" in p_lower or "project" in p_lower:
            project_name = "Task and Project Manager"
            slug = "task-project-manager"
            entities = [
                {"entity": "User", "fields": ["id", "username", "email", "role", "created_at"]},
                {"entity": "Project", "fields": ["id", "title", "description", "status", "created_at"]},
                {"entity": "Task", "fields": ["id", "project_id", "title", "description", "status", "priority", "due_date", "assigned_to"]}
            ]
            pages = ["Dashboard", "KanbanBoard", "TaskList", "Projects", "Team", "Login"]
            roles = ["Admin", "ProjectManager", "Developer"]
        else:
            words = [w.capitalize() for w in re.findall(r'\b[a-zA-Z]{3,}\b', prompt)[:4]]
            project_name = f"{' '.join(words) if words else 'AutoDev Application'}"
            slug = self._generate_slug(project_name)
            entities = [
                {"entity": "User", "fields": ["id", "username", "email", "role", "created_at"]},
                {"entity": "Item", "fields": ["id", "title", "description", "category", "status", "created_at", "updated_at"]},
                {"entity": "Log", "fields": ["id", "item_id", "action", "timestamp", "performed_by"]}
            ]
            pages = ["Dashboard", "Items", "Analytics", "Settings", "Login"]
            roles = ["Admin", "User"]

        return {
            "project_name": project_name,
            "project_slug": slug,
            "project_description": f"A full-stack, responsive web application for {project_name.lower()} featuring real-time dashboard analytics, complete CRUD workflows, search and filtering, and SQLite database persistence.",
            "target_users": ["System Administrators", "Operational Staff", "General Users"],
            "user_roles": roles,
            "features": [
                {"id": "feat_auth", "title": "Authentication & Role Access", "description": "Admin login, session authorization, and permission control.", "priority": "high"},
                {"id": "feat_crud", "title": "Comprehensive CRUD Management", "description": "Create, read, update, search, and delete domain records with instant form validation.", "priority": "high"},
                {"id": "feat_analytics", "title": "Dashboard Metrics & Statistics", "description": "Overview KPIs, status distribution cards, and real-time summary statistics.", "priority": "high"},
                {"id": "feat_search", "title": "Fast Search and Filter", "description": "Client & server side search by keywords, categories, and date ranges.", "priority": "medium"},
                {"id": "feat_export", "title": "Data Export and Activity History", "description": "Track history logs and quick status transitions.", "priority": "medium"}
            ],
            "pages": pages,
            "components": ["Navbar", "Sidebar", "StatsCard", "DataTable", "FormModal", "SearchFilterBar", "ToastNotification", "ConfirmDialog"],
            "api_requirements": [
                {"endpoint": "/api/auth/login", "method": "POST", "purpose": "Authenticate user credentials"},
                {"endpoint": "/api/stats", "method": "GET", "purpose": "Retrieve summary analytics and KPI counters"},
                {"endpoint": "/api/items", "method": "GET", "purpose": "List records with search and filter parameters"},
                {"endpoint": "/api/items", "method": "POST", "purpose": "Create a new record"},
                {"endpoint": "/api/items/<id>", "method": "PUT", "purpose": "Update an existing record"},
                {"endpoint": "/api/items/<id>", "method": "DELETE", "purpose": "Delete a record"}
            ],
            "database_entities": entities,
            "authentication_requirements": {
                "method": "Session / Token with demo credentials",
                "default_admin": {"username": "admin", "password": "admin123", "role": "Admin"}
            },
            "validation_requirements": [
                "Required fields validation on all entity forms",
                "Email format integrity verification",
                "Unique constraint enforcement on key identifier fields",
                "Sanitization of search strings to prevent injection"
            ],
            "non_functional_requirements": [
                "SQLite local database with automatic schema creation (db.create_all())",
                "Full-duplex CORS support between frontend (5173/dynamic) and backend (5000/dynamic)",
                "Fluid dark-mode glassmorphic user interface with modern typography",
                "Pure Vanilla CSS with zero extraneous UI framework baggage for maximum reliability",
                "React + Vite fast bundle compilation"
            ]
        }

requirement_agent = RequirementAgent()
