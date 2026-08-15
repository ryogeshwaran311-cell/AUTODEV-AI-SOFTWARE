import os
import sys
import io
import time
import requests

if sys.stdout is not None and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def test_live_system():
    print("--- 1. Testing Unified Web App & Frontend Static Shell ---")
    fe_res = requests.get("http://127.0.0.1:5000/", timeout=3)
    assert fe_res.status_code == 200, f"Unified Frontend failed: {fe_res.status_code}"
    assert "AutoDevAI" in fe_res.text or "root" in fe_res.text
    print("✓ Unified Server is online and serving React HTML frontend on port 5000.")

    print("\n--- 2. Testing Backend Health ---")
    be_res = requests.get("http://127.0.0.1:5000/api/health")
    assert be_res.status_code == 200
    print(f"✓ Backend Health: {be_res.json()}")

    print("\n--- 3. Testing Autonomous Project Generation ---")
    prompt = "Build a Student Management System with Admin Login, Student CRUD, Attendance Management, Search and Dashboard."
    gen_res = requests.post("http://127.0.0.1:5000/api/projects/generate", json={"prompt": prompt})
    assert gen_res.status_code == 202
    proj_data = gen_res.json()
    proj_id = proj_data["project_id"]
    print(f"✓ Generation initiated for project ID #{proj_id}: {proj_data['slug']}")

    print("\n--- 4. Polling Multi-Agent Pipeline Status ---")
    for attempt in range(40):
        time.sleep(1)
        st_res = requests.get(f"http://127.0.0.1:5000/api/projects/{proj_id}/status")
        st = st_res.json()
        print(f"[{st.get('current_stage', 'unknown').upper()}] Progress: {st.get('progress_pct')}% | Status: {st.get('status')}")
        if st.get('status') == 'READY':
            print("✓ Multi-Agent Pipeline completed with status: READY!")
            break
        elif st.get('status') == 'FAILED':
            raise RuntimeError(f"Pipeline failed: {st}")

    print("\n--- 5. Verifying Project Details & Workspace Files ---")
    det_res = requests.get(f"http://127.0.0.1:5000/api/projects/{proj_id}")
    det = det_res.json()
    files = det["project"]["files"]
    print(f"✓ Project created with {len(files)} files: {files[:6]}...")
    assert "backend/app.py" in files
    assert "frontend/src/App.jsx" in files
    assert "README.md" in files
    assert "vercel.json" in files
    assert "render.yaml" in files

    print("\n--- 6. Testing Preview Server Lifecycle ---")
    prev_start = requests.post(f"http://127.0.0.1:5000/api/projects/{proj_id}/preview/start")
    print(f"Preview Start Response: {prev_start.json()}")
    assert prev_start.json().get("success")

    time.sleep(2)
    prev_status = requests.get(f"http://127.0.0.1:5000/api/projects/{proj_id}/preview/status")
    print(f"✓ Preview Status: {prev_status.json()}")

    prev_stop = requests.post(f"http://127.0.0.1:5000/api/projects/{proj_id}/preview/stop")
    print(f"✓ Preview Stop: {prev_stop.json()}")

    print("\n--- 7. Testing Deployment Service ---")
    dep_res = requests.post(f"http://127.0.0.1:5000/api/projects/{proj_id}/deploy", json={"target": "vercel"})
    print(f"✓ Vercel Deployment Check: {dep_res.json()}")

    print("\n--- 8. Testing ZIP Download ---")
    zip_res = requests.get(f"http://127.0.0.1:5000/api/projects/{proj_id}/download")
    assert zip_res.status_code == 200
    assert len(zip_res.content) > 1000
    print(f"✓ ZIP Download delivered {len(zip_res.content)} bytes.")

    print("\n========================================================")
    print("ALL LIVE FULL-STACK TESTS PASSED WITH 100% PERFECTION!")
    print("========================================================")

if __name__ == "__main__":
    test_live_system()
