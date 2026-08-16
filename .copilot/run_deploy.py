"""
Run a Render deployment for a project under projects/<project_name> using the
RENDER_API_KEY environment variable (falls back to credentials if provided).

Usage:
  python ./.copilot/run_deploy.py <project_name>

Prints the deployment_service.deploy() result as JSON to stdout.
"""
import os
import sys
import json
from pathlib import Path

if len(sys.argv) < 2:
    print(json.dumps({"error": "project_name argument required"}))
    sys.exit(2)

project_name = sys.argv[1]
repo_root = Path(__file__).resolve().parents[1]
project_path = str(repo_root / 'projects' / project_name)

# Ensure repo root is on sys.path and import deployment_service
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)
try:
    from backend.services.deployment_service import deployment_service
except Exception as e:
    print(json.dumps({"error": "import_failed", "details": str(e)}))
    raise

# Call deploy (it will read RENDER_API_KEY from env if credentials not provided)
try:
    result = deployment_service.deploy(project_path, target='render', credentials={})
    # Remove any obvious sensitive fields from result before printing (defensive)
    safe_result = dict(result)
    if isinstance(safe_result.get('git_synced'), str):
        safe_result['git_synced'] = safe_result.get('git_synced')
    # Print JSON
    print(json.dumps(safe_result))
except Exception as e:
    print(json.dumps({"error": "deploy_failed", "details": str(e)}))
    raise
