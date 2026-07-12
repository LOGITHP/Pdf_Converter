import os
import logging
import subprocess
from PIL import Image
import fitz # PyMuPDF
from backend.converters.base import BaseConverter
from backend.utils import sys_info

logger = logging.getLogger("ocr_engine")

class OCREngine(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        # Can OCR PDFs or images into Searchable PDFs
        if from_ext in ["pdf", "png", "jpg", "jpeg", "tiff", "bmp"]:
            return to_ext == "pdf"
        return False

    def is_available(self) -> bool:
        return sys_info.get_engine_path("tesseract") is not None

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        tess_path = sys_info.get_engine_path("tesseract")
        if not tess_path:
            raise RuntimeError("The application installation is corrupted. Please reinstall.")

        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        logger.info(f"Running local OCR on: {input_path}")
        
        # Configure pytesseract to use detected tesseract path
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tess_path
        except ImportError:
            raise ImportError("Python package 'pytesseract' is not installed. Please install it.")

        # OCR individual image to PDF
        if from_ext in ["png", "jpg", "jpeg", "tiff", "bmp"]:
            return self._ocr_image_to_pdf(input_path, output_path, pytesseract)

        # OCR PDF to Searchable PDF
        if from_ext == "pdf":
            return self._ocr_pdf_to_searchable_pdf(input_path, output_path, pytesseract)

        return False

    def _ocr_image_to_pdf(self, input_path: str, output_path: str, pytesseract) -> bool:
        try:
            img = Image.open(input_path)
            # Run Tesseract OCR and output PDF bytes directly
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
            img.close()
            return True
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise RuntimeError(f"OCR processing failed: {e}")

    def _ocr_pdf_to_searchable_pdf(self, input_path: str, output_path: str, pytesseract) -> bool:
        doc = fitz.open(input_path)
        temp_pages = []
        try:
            out_dir = os.path.dirname(output_path)
            
            # Loop through each page, render to image, run OCR, save page PDF
            for p in range(len(doc)):
                logger.info(f"OCRing page {p+1}/{len(doc)}")
                page = doc.load_page(p)
                
                # Render to high-res image (dpi=200 is optimal for Tesseract)
                pix = page.get_pixmap(dpi=200)
                img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Run OCR
                ocr_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img_data, extension='pdf')
                
                # Save temp page PDF
                page_temp_path = os.path.join(out_dir, f"_ocr_temp_page_{p}.pdf")
                with open(page_temp_path, "wb") as f:
                    f.write(ocr_pdf_bytes)
                temp_pages.append(page_temp_path)
                
            # Merge temp pages
            result_doc = fitz.open()
            for path in temp_pages:
                page_doc = fitz.open(path)
                result_doc.insert_pdf(page_doc)
                page_doc.close()
                
            result_doc.save(output_path)
            result_doc.close()
            return True
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            raise RuntimeError(f"PDF OCR processing failed: {e}")
        finally:
            doc.close()
            # Clean up temp files
            for p in temp_pages:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass
