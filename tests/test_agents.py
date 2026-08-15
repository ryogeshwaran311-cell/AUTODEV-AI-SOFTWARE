import os
import sys
import unittest
import shutil

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.requirement_agent import requirement_agent
from backend.services.planning_agent import planning_agent
from backend.services.coding_agent import coding_agent
from backend.services.project_generator import project_generator
from backend.services.testing_agent import testing_agent
from backend.services.repair_agent import repair_agent
from backend.services.documentation_agent import documentation_agent
from backend.services.validator import final_validator
from backend.services.zip_service import zip_service

class TestAutoDevAIAgents(unittest.TestCase):
    def setUp(self):
        self.prompt = "Build a Student Management System with Admin Login, Student CRUD, Attendance Management, Search and Dashboard."
        self.test_slug = "test-student-system"
        self.test_workspace = os.path.join(project_generator.base_dir, self.test_slug)
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace, ignore_errors=True)

    def tearDown(self):
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace, ignore_errors=True)

    def test_full_agent_pipeline_e2e(self):
        # 1. Requirement Agent
        reqs = requirement_agent.analyze(self.prompt)
        self.assertIn("project_name", reqs)
        self.assertIn("features", reqs)
        self.assertTrue(len(reqs["features"]) > 0)

        # 2. Planning Agent
        plan = planning_agent.plan(reqs)
        self.assertIn("database_models", plan)
        self.assertIn("api_endpoints", plan)
        self.assertTrue(len(plan["database_models"]) > 0)

        # 3. Coding Agent
        files = coding_agent.generate_project_files(reqs, plan)
        self.assertIn("backend/app.py", files)
        self.assertIn("frontend/src/App.jsx", files)
        self.assertIn("frontend/package.json", files)

        # Verify no markdown code fences
        for path, code in files.items():
            self.assertFalse(code.strip().startswith("```"), f"File {path} contains raw code fence")

        # 4. Project Generator
        ws_info = project_generator.create_project_workspace(
            project_slug=self.test_slug,
            files=files,
            metadata={"name": reqs.get("project_name"), "prompt": self.prompt}
        )
        self.assertTrue(os.path.isdir(ws_info["project_path"]))
        self.assertTrue(os.path.isfile(os.path.join(ws_info["project_path"], "backend", "app.py")))

        # 5. Testing Agent
        test_res = testing_agent.run_tests(ws_info["project_path"])
        self.assertTrue(test_res["passed"], f"Test QA failed: {test_res.get('errors')}")

        # 6. Documentation Agent
        readme_str = documentation_agent.generate_readme(ws_info["project_path"], reqs, plan)
        self.assertTrue(os.path.isfile(os.path.join(ws_info["project_path"], "README.md")))
        self.assertIn("Student", readme_str)

        # 7. Final Validator
        val_res = final_validator.validate(ws_info["project_path"])
        self.assertTrue(val_res["is_valid"], f"Validation failed: {val_res}")
        self.assertEqual(val_res["status"], "READY")

        # 8. ZIP Service
        zip_path, filename, size_bytes = zip_service.create_project_zip(ws_info["project_path"], self.test_slug)
        self.assertTrue(os.path.isfile(zip_path))
        self.assertTrue(size_bytes > 0)
        os.remove(zip_path)

if __name__ == "__main__":
    unittest.main()
