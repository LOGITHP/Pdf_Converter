import os
import logging
from backend.converters.office.office_converter import OfficeConverter
from backend.converters.spreadsheets.sheet_converter import SheetConverter
from backend.converters.presentations.slides_converter import SlidesConverter
from backend.converters.pdf.pdf_converter import PDFConverter
from backend.converters.images.image_converter import ImageConverter
from backend.converters.notebooks.notebook_converter import NotebookConverter
from backend.converters.code.code_converter import CodeConverter
from backend.converters.text.text_converter import TextConverter
from backend.converters.ocr.ocr_engine import OCREngine
from backend.converters.metadata.metadata_engine import MetadataEngine
from backend.converters.compression.compression_engine import CompressionEngine

logger = logging.getLogger("router")

class ConversionRouter:
    def __init__(self):
        # Register all converters in order of priority (most specific first)
        self.converters = [
            CompressionEngine(),
            MetadataEngine(),
            OCREngine(),
            PDFConverter(),
            ImageConverter(),
            OfficeConverter(),
            SheetConverter(),
            SlidesConverter(),
            NotebookConverter(),
            CodeConverter(),
            TextConverter()
        ]

    def get_converter(self, from_ext: str, to_ext: str, options: dict = None) -> tuple:
        """
        Finds the best available converter for from_ext -> to_ext.
        Returns (converter, name) or (None, None) if not supported.
        """
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        options = options or {}

        # 1. Special flag: if OCR requested, check if OCREngine is available
        if options.get("ocr", False):
            ocr = self._find_converter(OCREngine, from_ext, to_ext)
            if ocr and ocr.is_available():
                return ocr, "OCR Engine (Tesseract)"

        # 2. Check if we need to do compression
        if options.get("operation") == "compress":
            comp = self._find_converter(CompressionEngine, from_ext, to_ext)
            if comp and comp.is_available():
                return comp, "Compression Engine"

        # 3. Check for specific layout converters (Office, PDF, spreadsheets, notebooks)
        # Iterate over converters and pick the first one that supports the route and is available
        for conv in self.converters:
            if isinstance(conv, (OCREngine, CompressionEngine, MetadataEngine)):
                if isinstance(conv, OCREngine) and not options.get("ocr"):
                    continue
                if isinstance(conv, CompressionEngine) and options.get("operation") != "compress":
                    continue
                if isinstance(conv, MetadataEngine) and options.get("operation") != "metadata":
                    continue

            if conv.can_convert(from_ext, to_ext):
                if conv.is_available():
                    # Return class name for logging
                    return conv, conv.__class__.__name__

        return None, None

    def _find_converter(self, cls, from_ext: str, to_ext: str):
        for conv in self.converters:
            if isinstance(conv, cls) and conv.can_convert(from_ext, to_ext):
                return conv
        return None

    def convert_file(self, input_path: str, output_path: str, options: dict = None) -> str:
        """
        Main routing method. Resolves converter, runs it, and returns the engine name.
        """
        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')
        options = options or {}

        conv, name = self.get_converter(from_ext, to_ext, options)
        if not conv:
            raise NotImplementedError(
                f"No conversion path or engine available for: .{from_ext} -> .{to_ext}"
            )

        logger.info(f"Routing .{from_ext} -> .{to_ext} to {name}")
        success = conv.convert(input_path, output_path, options)
        if not success:
            raise RuntimeError(f"Conversion using {name} failed.")

        return name
