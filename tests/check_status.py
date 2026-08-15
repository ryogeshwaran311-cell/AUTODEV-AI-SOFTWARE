import time, requests

time.sleep(4)
r = requests.get('http://127.0.0.1:5000/api/projects/5/status')
d = r.json()
print(f"stage: {d['current_stage']} | pct: {d['progress_pct']}% | status: {d['status']}")
for log in d.get('logs', []):
    print(f"  LOG [{log['stage']}] [{log['level']}] {log['message']}")
