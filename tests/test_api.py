import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.database import db

import tempfile

class TestAutoDevAIAPI(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.environ['AUTODEVAI_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
        try:
            os.close(self.db_fd)
            os.remove(self.db_path)
        except Exception:
            pass

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('app'), 'AutoDevAI Platform')

    def test_config_endpoint(self):
        response = self.client.get('/api/config')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('gemini_model', data)

    def test_list_projects_empty(self):
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIsInstance(data.get('projects'), list)

    def test_generate_project_validation(self):
        response = self.client.post('/api/projects/generate', json={})
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/projects/generate', json={"prompt": "Build a Simple CRM with Contacts and Deals"})
        self.assertEqual(response.status_code, 202)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('project_id', data)

if __name__ == "__main__":
    unittest.main()
