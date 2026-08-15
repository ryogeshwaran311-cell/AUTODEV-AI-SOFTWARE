import os
import sys
import time
import requests

# Ensure project root in sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.services.preview_service import preview_service
from backend.services.deployment_service import deployment_service

def test_full_system():
    print("=== 1. Testing Preview Service on create-calculator ===")
    project_path = os.path.abspath(os.path.join(ROOT, "generated_projects", "create-calculator"))
    
    start_res = preview_service.start_preview(9999, project_path)
    print("Start Preview Result:", start_res)
    assert start_res.get("success") == True, f"Failed to start preview: {start_res}"
    
    fe_port = start_res["frontend_port"]
    be_port = start_res["backend_port"]
    fe_url = start_res["preview_url"]
    be_url = f"http://127.0.0.1:{be_port}"

    print(f"Polling endpoints: Frontend={fe_url}, Backend={be_url}")
    time.sleep(3)

    # Check preview status
    status = preview_service.get_status(9999)
    print("Preview Service Status:", status)
    assert status.get("active") == True, "Preview service is not active"

    # Test HTTP GET on Backend API
    try:
        r_be = requests.get(f"{be_url}/api/health", timeout=5)
        print(f"Backend /api/health -> HTTP {r_be.status_code}: {r_be.json()}")
        assert r_be.status_code == 200, f"Backend health check failed: {r_be.status_code}"
    except Exception as be_err:
        print("Backend request error:", be_err)
        raise

    # Test HTTP GET on Frontend Dev Server
    try:
        r_fe = requests.get(fe_url, timeout=5)
        print(f"Frontend {fe_url} -> HTTP {r_fe.status_code}, Length: {len(r_fe.text)}")
        assert r_fe.status_code == 200, f"Frontend request failed: {r_fe.status_code}"
        assert "<!doctype html>" in r_fe.text.lower() or "<html" in r_fe.text.lower()
    except Exception as fe_err:
        print("Frontend request error:", fe_err)
        raise

    # Stop preview
    stop_res = preview_service.stop_preview(9999)
    print("Stop Preview Result:", stop_res)

    print("\n=== 2. Testing Unified Deployment Service ===")
    dep_prep = deployment_service.prepare_deployment(project_path)
    print("Deployment Prep:", dep_prep)
    assert dep_prep.get("has_render_config") == True, "Missing render.yaml"
    assert dep_prep.get("has_vercel_config") == True, "Missing vercel.json"

    dep_res = deployment_service.deploy(project_path, target="render")
    print("Deploy Result (Render Full-Stack):", dep_res)
    assert dep_res.get("success") == True, "Render deploy failed"
    assert "Render Full-Stack" in dep_res.get("target", "")

    print("\n>>> ALL SYSTEM VERIFICATIONS PASSED 100%! <<<")

if __name__ == "__main__":
    test_full_system()
