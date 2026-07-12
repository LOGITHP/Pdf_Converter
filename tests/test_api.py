import unittest
import sys
import os
from fastapi.testclient import TestClient

# Insert workspace root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "app": "UniversalConverter"})

    def test_status_endpoint(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("os", data)
        self.assertIn("python_version", data)
        self.assertIn("engines", data)
        
        engines = data["engines"]
        self.assertIn("libreoffice", engines)
        self.assertIn("tesseract", engines)
        self.assertIn("ghostscript", engines)
        self.assertIn("poppler", engines)
        self.assertIn("imagemagick", engines)
        self.assertIn("pandoc", engines)
        self.assertIn("ffmpeg", engines)

    def test_invalid_conversion_route(self):
        # DOCX to IPYNB is not supported
        response = self.client.post(
            "/api/convert",
            data={"to_ext": "ipynb", "ocr": "false"},
            files={"file": ("test.docx", b"dummy contents", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("not supported", response.json()["detail"].lower())

if __name__ == "__main__":
    unittest.main()
