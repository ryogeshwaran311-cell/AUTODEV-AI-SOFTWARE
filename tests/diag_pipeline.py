import sys, os
sys.path.insert(0, '.')
os.environ.setdefault('GEMINI_API_KEY', '')

from backend.services.requirement_agent import requirement_agent
from backend.services.planning_agent import planning_agent
from backend.services.coding_agent import coding_agent
from backend.services.project_generator import project_generator
from backend.services.testing_agent import testing_agent
from backend.services.repair_agent import repair_agent
from backend.services.documentation_agent import documentation_agent
from backend.services.validator import final_validator

prompt = "Build a Student Management System with Admin Login, Student CRUD, Attendance Management, Search and Dashboard."

print("[1] Running RequirementAgent...")
req = requirement_agent.analyze(prompt)
print(f"    project_name: {req.get('project_name')}")
print(f"    slug: {req.get('project_slug')}")
print(f"    features: {len(req.get('features', []))}")

print("[2] Running PlanningAgent...")
plan = planning_agent.plan(req)
print(f"    models: {len(plan.get('database_models', []))}")
print(f"    endpoints: {len(plan.get('api_endpoints', []))}")

print("[3] Running CodingAgent...")
files = coding_agent.generate_project_files(req, plan)
print(f"    files generated: {len(files)}")
print(f"    sample keys: {sorted(files.keys())[:8]}")

print("[4] Running ProjectGenerator...")
ws = project_generator.create_project_workspace(
    project_slug='diag-test-run-001',
    files=files,
    metadata={'name': req.get('project_name'), 'prompt': prompt}
)
print(f"    path: {ws['project_path']}")
print(f"    files_written: {ws['files_written']}")

print("[5] Running TestingAgent...")
test_res = testing_agent.run_tests(ws['project_path'])
print(f"    passed: {test_res.get('passed')}, checks: {test_res.get('checks_run')}")
if test_res.get('errors'):
    print(f"    errors: {test_res['errors'][:3]}")

print("[6] Running DocumentationAgent...")
readme = documentation_agent.generate_readme(ws['project_path'], req, plan)
print(f"    README length: {len(readme)} chars")

print("[7] Running FinalValidator...")
val = final_validator.validate(ws['project_path'])
print(f"    is_valid: {val.get('is_valid')}, score: {val.get('score_pct')}%")

print("")
print("=" * 50)
print("ALL PIPELINE STAGES COMPLETED SUCCESSFULLY!")
print("=" * 50)
