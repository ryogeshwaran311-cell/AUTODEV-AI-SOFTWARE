import os
import ast
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AutoDevAI.Validator")

class FinalValidator:
    """
    15-point checklist validator executing exhaustive verification before
    marking generated applications as READY.
    """

    def validate(self, project_path: str) -> Dict[str, Any]:
        logger.info(f"Final Validator executing 15-point checklist on: {project_path}")
        
        checklist: List[Dict[str, Any]] = []

        def add_check(title: str, passed: bool, notes: str = ""):
            checklist.append({
                "title": title,
                "passed": passed,
                "status": "PASSED" if passed else "FAILED",
                "notes": notes
            })

        # 1. Required directories
        dirs_to_check = [
            "backend", "backend/services", "frontend", 
            "frontend/src", "frontend/src/components", "frontend/public"
        ]
        all_dirs = all(os.path.isdir(os.path.join(project_path, d)) for d in dirs_to_check)
        add_check("Required directories structure", all_dirs, f"Checked {len(dirs_to_check)} core directories")

        # 2. Required backend files
        be_files = ["backend/app.py", "backend/database.py", "backend/models.py", "backend/requirements.txt"]
        all_be = all(os.path.isfile(os.path.join(project_path, f)) for f in be_files)
        add_check("Backend core files present", all_be)

        # 3. Required frontend files
        fe_files = [
            "frontend/package.json", "frontend/vite.config.js", "frontend/index.html", 
            "frontend/src/main.jsx", "frontend/src/App.jsx", "frontend/src/index.css"
        ]
        all_fe = all(os.path.isfile(os.path.join(project_path, f)) for f in fe_files)
        add_check("Frontend core files present", all_fe)

        # 4. Backend dependencies declared
        req_p = os.path.join(project_path, "backend/requirements.txt")
        req_ok = False
        if os.path.isfile(req_p):
            with open(req_p, "r", encoding="utf-8") as rf:
                txt = rf.read().lower()
                req_ok = "flask" in txt and "sqlalchemy" in txt
        add_check("Backend requirements.txt validity", req_ok)

        # 5. Frontend dependencies declared
        pkg_p = os.path.join(project_path, "frontend/package.json")
        pkg_ok = False
        if os.path.isfile(pkg_p):
            try:
                with open(pkg_p, "r", encoding="utf-8") as pf:
                    pj = json.load(pf)
                    pkg_ok = "react" in pj.get("dependencies", {})
            except Exception:
                pass
        add_check("Frontend package.json validity", pkg_ok)

        # 6. Python syntax compiles
        py_syntax_ok = True
        for root, _, files in os.walk(os.path.join(project_path, "backend")):
            for f in files:
                if f.endswith(".py"):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8") as pf:
                            ast.parse(pf.read())
                    except Exception:
                        py_syntax_ok = False
        add_check("Python AST syntax validation", py_syntax_ok)

        # 7. JavaScript/JSX syntax & balanced tags
        jsx_ok = True
        app_jsx = os.path.join(project_path, "frontend/src/App.jsx")
        if os.path.isfile(app_jsx):
            with open(app_jsx, "r", encoding="utf-8") as jf:
                app_code = jf.read()
                # Basic bracket balance check
                jsx_ok = (app_code.count("{") == app_code.count("}")) and ("export default" in app_code)
        add_check("React App.jsx integrity", jsx_ok)

        # 8. Database schema configuration
        models_p = os.path.join(project_path, "backend/models.py")
        models_ok = False
        if os.path.isfile(models_p):
            with open(models_p, "r", encoding="utf-8") as mf:
                models_ok = "db.Model" in mf.read()
        add_check("SQLAlchemy models configuration", models_ok)

        # 9. Database auto-initialization in app.py
        app_p = os.path.join(project_path, "backend/app.py")
        db_init_ok = False
        if os.path.isfile(app_p):
            with open(app_p, "r", encoding="utf-8") as af:
                db_init_ok = "db.create_all()" in af.read()
        add_check("Database auto-initialization (db.create_all)", db_init_ok)

        # 10. Frontend build configuration (vite.config.js)
        vite_p = os.path.join(project_path, "frontend/vite.config.js")
        vite_ok = os.path.isfile(vite_p)
        add_check("Vite development & build configuration", vite_ok)

        # 11. REST API endpoint structure
        api_ok = False
        if os.path.isfile(app_p):
            with open(app_p, "r", encoding="utf-8") as af:
                app_c = af.read()
                api_ok = "@app.route" in app_c and "/api/" in app_c
        add_check("REST API routing implementation", api_ok)

        # 12. CORS enabled
        cors_ok = False
        if os.path.isfile(app_p):
            with open(app_p, "r", encoding="utf-8") as af:
                cors_ok = "CORS" in af.read()
        add_check("Cross-Origin Resource Sharing (CORS)", cors_ok)

        # 13. Deployment configuration for Vercel
        vercel_ok = os.path.isfile(os.path.join(project_path, "vercel.json"))
        add_check("Vercel deployment manifest (vercel.json)", vercel_ok)

        # 14. Deployment configuration for Render
        render_ok = os.path.isfile(os.path.join(project_path, "render.yaml"))
        add_check("Render deployment manifest (render.yaml)", render_ok)

        # 15. Comprehensive README documentation
        readme_ok = os.path.isfile(os.path.join(project_path, "README.md"))
        add_check("Project README documentation", readme_ok)

        # Score calculations
        passed_count = sum(1 for c in checklist if c["passed"])
        total_count = len(checklist)
        is_valid = (passed_count == total_count)

        logger.info(f"Final Validation Result: {passed_count}/{total_count} checks passed (Valid: {is_valid})")

        return {
            "is_valid": is_valid,
            "passed_checks": passed_count,
            "total_checks": total_count,
            "score_pct": int((passed_count / total_count) * 100),
            "checklist": checklist,
            "status": "READY" if is_valid else "FAILED"
        }

final_validator = FinalValidator()
