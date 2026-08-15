import os
import logging
from typing import Dict, Any, List
from backend.services.gemini_service import gemini_service
from backend.services.testing_agent import testing_agent

logger = logging.getLogger("AutoDevAI.RepairAgent")

class RepairAgent:
    """
    Repair Agent inspects test failures, applies targeted fixes to files,
    and runs a bounded verification loop (max 3 attempts).
    """

    MAX_REPAIR_ATTEMPTS = 3

    def repair(self, project_path: str, initial_test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes bounded repair loop.
        Returns: {"repaired": bool, "attempts": int, "final_test_results": dict, "actions": []}
        """
        current_results = initial_test_results
        actions: List[str] = []
        attempt = 0

        while not current_results.get("passed", False) and attempt < self.MAX_REPAIR_ATTEMPTS:
            attempt += 1
            errors = current_results.get("errors", [])
            logger.info(f"Repair Agent starting attempt {attempt}/{self.MAX_REPAIR_ATTEMPTS} to fix {len(errors)} issues")

            for err in errors:
                stage = err.get("stage")
                
                # Case 1: Missing essential Python dependency
                if stage == "python_deps":
                    req_path = os.path.join(project_path, "backend", "requirements.txt")
                    if os.path.isfile(req_path):
                        with open(req_path, "r", encoding="utf-8") as rf:
                            content = rf.read()
                        needed = ["flask>=3.0.0", "flask-cors>=4.0.0", "flask-sqlalchemy>=3.1.1", "python-dotenv>=1.0.0"]
                        for dep in needed:
                            pkg_name = dep.split(">=")[0]
                            if pkg_name not in content:
                                content += f"\n{dep}"
                                actions.append(f"Added {dep} to backend/requirements.txt")
                        with open(req_path, "w", encoding="utf-8") as wf:
                            wf.write(content.strip() + "\n")

                # Case 2: Code artifacts / markdown fences
                elif stage == "code_cleanliness":
                    for detail in err.get("details", []):
                        if "contains raw markdown" in detail:
                            rel_file = detail.split()[0]
                            full_path = os.path.join(project_path, rel_file)
                            if os.path.isfile(full_path):
                                with open(full_path, "r", encoding="utf-8") as f:
                                    code = f.read()
                                cleaned = gemini_service.clean_markdown_fences(code)
                                with open(full_path, "w", encoding="utf-8") as f:
                                    f.write(cleaned)
                                actions.append(f"Cleaned markdown fences from {rel_file}")

                # Case 3: Missing CORS in backend/app.py
                elif stage == "cors":
                    app_path = os.path.join(project_path, "backend", "app.py")
                    if os.path.isfile(app_path):
                        with open(app_path, "r", encoding="utf-8") as f:
                            code = f.read()
                        if "from flask_cors import CORS" not in code:
                            code = "from flask_cors import CORS\n" + code
                        if "CORS(app)" not in code:
                            code = code.replace("app = Flask(__name__)", "app = Flask(__name__)\n    CORS(app, resources={r'/*': {'origins': '*'}})")
                        with open(app_path, "w", encoding="utf-8") as f:
                            f.write(code)
                        actions.append("Injected Flask-CORS configuration into backend/app.py")

                # Case 4: Python syntax error repair
                elif stage == "python_syntax":
                    for detail in err.get("details", []):
                        rel_file = detail.get("file")
                        err_msg = detail.get("error")
                        full_path = os.path.join(project_path, rel_file)
                        if os.path.isfile(full_path):
                            with open(full_path, "r", encoding="utf-8") as f:
                                buggy_code = f.read()
                            
                            # Attempt repair with Gemini or automatic cleanup
                            repaired_code = None
                            if gemini_service.is_configured():
                                try:
                                    prompt = f"Fix this Python syntax error in {rel_file}:\nError: {err_msg}\n\nCode:\n{buggy_code}\n\nReturn ONLY valid Python code with NO markdown formatting."
                                    repaired_code = gemini_service.generate_text(prompt, temperature=0.1)
                                    repaired_code = gemini_service.clean_markdown_fences(repaired_code)
                                except Exception as gemini_err:
                                    logger.warning(f"Repair Agent Gemini error repair failed: {gemini_err}")

                            if not repaired_code:
                                repaired_code = gemini_service.clean_markdown_fences(buggy_code)

                            with open(full_path, "w", encoding="utf-8") as f:
                                f.write(repaired_code)
                            actions.append(f"Repaired syntax in {rel_file}")

            # Re-run test suite after repairs
            current_results = testing_agent.run_tests(project_path)

        repaired_success = current_results.get("passed", False)
        return {
            "repaired": repaired_success,
            "attempts": attempt,
            "actions_taken": actions,
            "final_test_results": current_results
        }

repair_agent = RepairAgent()
