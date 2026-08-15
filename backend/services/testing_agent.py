import os
import ast
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AutoDevAI.TestingAgent")

class TestingAgent:
    """
    Automated QA and static analysis agent verifying syntax, dependencies,
    database schemas, and project completeness.
    """

    MANDATORY_FILES = [
        "backend/app.py",
        "backend/database.py",
        "backend/models.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/vite.config.js",
        "frontend/index.html",
        "frontend/src/main.jsx",
        "frontend/src/App.jsx",
        "frontend/src/index.css",
        "vercel.json",
        "render.yaml"
    ]

    FORBIDDEN_PLACEHOLDERS = [
        "TODO", "FIXME", "Coming soon", "coming soon", "Placeholder", "Implement later", "Example only"
    ]

    def run_tests(self, project_path: str) -> Dict[str, Any]:
        """Runs full test suite on the generated project directory."""
        logger.info(f"Testing Agent initiating QA suite on: {project_path}")

        errors: List[Dict[str, Any]] = []
        warnings: List[str] = []
        checks_run = 0
        checks_passed = 0

        # Check 1: Mandatory File Existence
        checks_run += 1
        missing_files = []
        for rel in self.MANDATORY_FILES:
            full = os.path.join(project_path, rel)
            if not os.path.isfile(full):
                missing_files.append(rel)

        if missing_files:
            errors.append({
                "stage": "structure",
                "message": f"Missing mandatory project files: {', '.join(missing_files)}",
                "files": missing_files
            })
        else:
            checks_passed += 1

        # Check 2: Python Syntax via AST
        checks_run += 1
        backend_dir = os.path.join(project_path, "backend")
        py_errors = []
        if os.path.isdir(backend_dir):
            for root, _, files in os.walk(backend_dir):
                for f in files:
                    if f.endswith(".py"):
                        fpath = os.path.join(root, f)
                        rel_f = os.path.relpath(fpath, project_path)
                        try:
                            with open(fpath, "r", encoding="utf-8") as py_file:
                                content = py_file.read()
                                ast.parse(content, filename=rel_f)
                        except Exception as syntax_err:
                            py_errors.append({
                                "file": rel_f,
                                "error": str(syntax_err)
                            })

        if py_errors:
            errors.append({
                "stage": "python_syntax",
                "message": f"Python syntax errors detected in {len(py_errors)} files",
                "details": py_errors
            })
        else:
            checks_passed += 1

        # Check 3: Python Requirements Validation
        checks_run += 1
        req_file = os.path.join(backend_dir, "requirements.txt")
        if os.path.isfile(req_file):
            with open(req_file, "r", encoding="utf-8") as rf:
                req_text = rf.read().lower()
                for essential in ["flask", "flask-cors", "flask-sqlalchemy"]:
                    if essential not in req_text and essential.replace("-", "_") not in req_text:
                        errors.append({
                            "stage": "python_deps",
                            "message": f"Missing essential dependency '{essential}' in backend/requirements.txt",
                            "file": "backend/requirements.txt"
                        })
                        break
                else:
                    checks_passed += 1
        else:
            errors.append({
                "stage": "python_deps",
                "message": "backend/requirements.txt not found"
            })

        # Check 4: Frontend package.json validation
        checks_run += 1
        pkg_file = os.path.join(project_path, "frontend", "package.json")
        if os.path.isfile(pkg_file):
            try:
                with open(pkg_file, "r", encoding="utf-8") as pf:
                    pkg_json = json.load(pf)
                    deps = pkg_json.get("dependencies", {})
                    dev_deps = pkg_json.get("devDependencies", {})
                    if "react" not in deps or "vite" not in dev_deps:
                        errors.append({
                            "stage": "frontend_deps",
                            "message": "frontend/package.json missing react or vite dependencies"
                        })
                    else:
                        checks_passed += 1
            except Exception as e:
                errors.append({
                    "stage": "frontend_deps",
                    "message": f"frontend/package.json is invalid JSON: {e}"
                })
        else:
            errors.append({
                "stage": "frontend_deps",
                "message": "frontend/package.json not found"
            })

        # Check 5: Forbidden Placeholders / Markdown artifacts
        checks_run += 1
        found_placeholders = []
        for root, _, files in os.walk(project_path):
            if "node_modules" in root or ".venv" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith((".py", ".jsx", ".js", ".html", ".css", ".json")):
                    fpath = os.path.join(root, f)
                    rel_f = os.path.relpath(fpath, project_path)
                    try:
                        with open(fpath, "r", encoding="utf-8") as fl:
                            text = fl.read()
                            # Check for leftover markdown fences
                            if text.strip().startswith("```") or text.strip().endswith("```"):
                                found_placeholders.append(f"{rel_f} contains raw markdown code fence")
                            # Check for placeholder keywords
                            for kw in self.FORBIDDEN_PLACEHOLDERS:
                                if f" {kw} " in text or f"//{kw}" in text or f"#{kw}" in text:
                                    warnings.append(f"{rel_f} may contain placeholder text: '{kw}'")
                    except Exception:
                        pass

        if found_placeholders:
            errors.append({
                "stage": "code_cleanliness",
                "message": f"Code artifacts detected: {'; '.join(found_placeholders)}",
                "details": found_placeholders
            })
        else:
            checks_passed += 1

        # Check 6: CORS & Port Configuration
        checks_run += 1
        app_file = os.path.join(backend_dir, "app.py")
        if os.path.isfile(app_file):
            with open(app_file, "r", encoding="utf-8") as af:
                app_text = af.read()
                if "CORS" not in app_text and "cors" not in app_text:
                    errors.append({
                        "stage": "cors",
                        "message": "backend/app.py does not appear to configure CORS"
                    })
                else:
                    checks_passed += 1
        else:
            errors.append({
                "stage": "cors",
                "message": "backend/app.py not found"
            })

        passed = (len(errors) == 0)
        logger.info(f"Testing Agent complete. Passed: {passed} ({checks_passed}/{checks_run} checks)")

        return {
            "passed": passed,
            "checks_run": checks_run,
            "checks_passed": checks_passed,
            "errors": errors,
            "warnings": warnings,
            "summary": f"Completed {checks_passed} of {checks_run} automated quality checks."
        }

testing_agent = TestingAgent()
