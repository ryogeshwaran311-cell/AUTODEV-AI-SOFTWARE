import os, sys
sys.path.insert(0, '.')
os.environ.setdefault('GEMINI_API_KEY', '')

from backend.app import app, db
from backend.models import Project
import threading

print('App created OK')

with app.app_context():
    print('Inside app context')
    p = Project.query.first()
    print('Query from main thread:', p)

    results = []

    def test_thread():
        with app.app_context():
            try:
                proj = db.session.get(Project, 1)
                results.append(('ok', str(proj)))
                print('Thread query OK:', proj)
            except Exception as e:
                results.append(('error', str(e)))
                print('Thread query FAILED:', e)
                import traceback; traceback.print_exc()

    t = threading.Thread(target=test_thread)
    t.start()
    t.join(timeout=10)
    print('Thread result:', results)
