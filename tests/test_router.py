import unittest
import sys
import os

# Insert workspace root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.router.router import ConversionRouter
from backend.converters.office.office_converter import OfficeConverter
from backend.converters.spreadsheets.sheet_converter import SheetConverter
from backend.converters.presentations.slides_converter import SlidesConverter
from backend.converters.pdf.pdf_converter import PDFConverter
from backend.converters.images.image_converter import ImageConverter
from backend.converters.notebooks.notebook_converter import NotebookConverter
from backend.converters.code.code_converter import CodeConverter
from backend.converters.text.text_converter import TextConverter

from unittest.mock import patch

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = ConversionRouter()
        self.patcher = patch("backend.utils.sys_info.get_engine_path", return_value="mock_path")
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_office_routing(self):
        conv, name = self.router.get_converter("docx", "pdf")
        self.assertIsInstance(conv, OfficeConverter)
        self.assertEqual(name, "OfficeConverter")

    def test_spreadsheet_routing(self):
        conv, name = self.router.get_converter("xlsx", "pdf")
        self.assertIsInstance(conv, SheetConverter)
        self.assertEqual(name, "SheetConverter")

        conv, name = self.router.get_converter("xlsx", "csv")
        self.assertIsInstance(conv, SheetConverter)

    def test_slides_routing(self):
        conv, name = self.router.get_converter("pptx", "pdf")
        self.assertIsInstance(conv, SlidesConverter)
        self.assertEqual(name, "SlidesConverter")

    def test_pdf_routing(self):
        conv, name = self.router.get_converter("pdf", "png")
        self.assertIsInstance(conv, PDFConverter)
        self.assertEqual(name, "PDFConverter")

    def test_image_routing(self):
        conv, name = self.router.get_converter("png", "jpg")
        self.assertIsInstance(conv, ImageConverter)
        self.assertEqual(name, "ImageConverter")

    def test_notebook_routing(self):
        conv, name = self.router.get_converter("ipynb", "html")
        self.assertIsInstance(conv, NotebookConverter)
        self.assertEqual(name, "NotebookConverter")

    def test_code_routing(self):
        conv, name = self.router.get_converter("py", "pdf")
        self.assertIsInstance(conv, CodeConverter)
        self.assertEqual(name, "CodeConverter")

    def test_text_routing(self):
        conv, name = self.router.get_converter("md", "pdf")
        self.assertIsInstance(conv, TextConverter)
        self.assertEqual(name, "TextConverter")

        conv, name = self.router.get_converter("txt", "pdf")
        self.assertIsInstance(conv, TextConverter)

if __name__ == "__main__":
    unittest.main()
