import os
import subprocess
import sys
import time

proj_dir = os.path.abspath('generated_projects/create-calculator/frontend')
target_nm = os.path.join(proj_dir, 'node_modules')
src_nm = os.path.abspath('frontend/node_modules')

print(f"Source node_modules: {src_nm}, exists: {os.path.exists(src_nm)}")

if not os.path.exists(target_nm):
    cmd = f'cmd /c mklink /J "{target_nm}" "{src_nm}"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("Junction result:", res.stdout, res.stderr)

local_vite_bin = os.path.join(src_nm, 'vite', 'bin', 'vite.js')
vite_cmd = ['node', local_vite_bin, '--port', '5200', '--host', '127.0.0.1']
p = subprocess.Popen(vite_cmd, cwd=proj_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(2)
poll = p.poll()
print("Vite process poll:", poll)
if poll is None:
    print("Vite is RUNNING successfully!")
    p.terminate()
    try:
        p.wait(timeout=2)
    except Exception:
        p.kill()
else:
    out, err = p.communicate()
    print("Vite failed:", err)
