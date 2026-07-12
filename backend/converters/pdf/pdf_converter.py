import os
import logging
import fitz  # PyMuPDF
from backend.converters.base import BaseConverter

logger = logging.getLogger("pdf_converter")

class PDFConverter(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        if from_ext == "pdf":
            return to_ext in ["pdf", "png", "jpg", "txt", "docx"]
        return False

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')
        options = options or {}
        
        if to_ext == "pdf":
            # Determine PDF-to-PDF sub-operation
            operation = options.get("operation", "copy")
            if operation == "compress":
                return self.compress_pdf(input_path, output_path, options.get("quality", 0.6))
            elif operation == "rotate":
                return self.rotate_pdf(input_path, output_path, options.get("rotation_angle", 90))
            elif operation == "extract":
                return self.extract_pages(input_path, output_path, options.get("pages_to_extract", []))
            elif operation == "watermark":
                return self.watermark_pdf(input_path, output_path, options.get("watermark_text", "CONFIDENTIAL"))
            elif operation == "encrypt":
                return self.encrypt_pdf(input_path, output_path, options.get("password", ""))
            elif operation == "decrypt":
                return self.decrypt_pdf(input_path, output_path, options.get("password", ""))
            else:
                # Default: copy/save
                import shutil
                shutil.copy2(input_path, output_path)
                return True
        elif to_ext in ["png", "jpg"]:
            return self.pdf_to_images(input_path, output_path, to_ext)
        elif to_ext == "txt":
            return self.pdf_to_text(input_path, output_path)
        elif to_ext == "docx":
            return self.pdf_to_docx(input_path, output_path)

        raise RuntimeError(f"Unsupported PDF conversion: .pdf -> .{to_ext}")

    def merge_pdfs(self, input_paths: list[str], output_path: str) -> bool:
        logger.info(f"Merging {len(input_paths)} PDF files into {output_path}")
        result_doc = fitz.open()
        try:
            for path in input_paths:
                doc = fitz.open(path)
                result_doc.insert_pdf(doc)
                doc.close()
            result_doc.save(output_path)
            return True
        finally:
            result_doc.close()

    def split_pdf(self, input_path: str, output_dir: str) -> list[str]:
        logger.info(f"Splitting PDF {input_path} into single pages in {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        doc = fitz.open(input_path)
        generated_paths = []
        try:
            basename = os.path.splitext(os.path.basename(input_path))[0]
            for p in range(len(doc)):
                page_doc = fitz.open()
                page_doc.insert_pdf(doc, from_page=p, to_page=p)
                out_path = os.path.join(output_dir, f"{basename}_page_{p+1}.pdf")
                page_doc.save(out_path)
                page_doc.close()
                generated_paths.append(out_path)
            return generated_paths
        finally:
            doc.close()

    def compress_pdf(self, input_path: str, output_path: str, quality: float = 0.6) -> bool:
        logger.info(f"Compressing PDF {input_path} (quality: {quality})")
        doc = fitz.open(input_path)
        try:
            # Save using garbage collection and compression options
            # deflate=True enables compression, garbage=3/4 releases unreferenced resources
            doc.save(output_path, garbage=3, deflate=True)
            return True
        finally:
            doc.close()

    def rotate_pdf(self, input_path: str, output_path: str, angle: int) -> bool:
        logger.info(f"Rotating PDF pages by {angle} degrees")
        doc = fitz.open(input_path)
        try:
            for page in doc:
                page.set_rotation((page.rotation + angle) % 360)
            doc.save(output_path)
            return True
        finally:
            doc.close()

    def extract_pages(self, input_path: str, output_path: str, pages: list[int]) -> bool:
        # pages is 1-indexed for users, convert to 0-indexed for fitz
        logger.info(f"Extracting pages {pages} from PDF")
        doc = fitz.open(input_path)
        out_doc = fitz.open()
        try:
            for p in pages:
                idx = p - 1
                if 0 <= idx < len(doc):
                    out_doc.insert_pdf(doc, from_page=idx, to_page=idx)
            out_doc.save(output_path)
            return True
        finally:
            doc.close()
            out_doc.close()

    def watermark_pdf(self, input_path: str, output_path: str, text: str) -> bool:
        logger.info(f"Watermarking PDF with text: {text}")
        doc = fitz.open(input_path)
        try:
            for page in doc:
                rect = page.rect
                # Put watermark diagonally in the middle of page
                # Using standard red color, 0.3 opacity, standard Helvetica font
                page.insert_textbox(
                    rect, 
                    text,
                    fontsize=50,
                    fontname="helv",
                    color=(1, 0, 0), # red
                    align=fitz.TEXT_ALIGN_CENTER,
                    rotate=45,
                    opacity=0.25
                )
            doc.save(output_path)
            return True
        finally:
            doc.close()

    def encrypt_pdf(self, input_path: str, output_path: str, password: str) -> bool:
        logger.info(f"Encrypting PDF with password protection")
        doc = fitz.open(input_path)
        try:
            # Set owner and user passwords
            doc.save(
                output_path, 
                encryption=fitz.PDF_ENCRYPT_AES_256, 
                user_pw=password, 
                owner_pw=password
            )
            return True
        finally:
            doc.close()

    def decrypt_pdf(self, input_path: str, output_path: str, password: str) -> bool:
        logger.info(f"Decrypting PDF using password")
        doc = fitz.open(input_path)
        try:
            if doc.is_encrypted:
                success = doc.authenticate(password)
                if not success:
                    raise RuntimeError("Incorrect password provided for decryption.")
            doc.save(output_path, encryption=fitz.PDF_ENCRYPT_KEEP)
            return True
        finally:
            doc.close()

    def pdf_to_images(self, input_path: str, output_path: str, fmt: str = "png") -> bool:
        logger.info(f"Converting first page of PDF to image format: {fmt}")
        doc = fitz.open(input_path)
        try:
            if len(doc) == 0:
                raise RuntimeError("PDF contains no pages.")
            page = doc.load_page(0) # convert page 0 (first page)
            pix = page.get_pixmap(dpi=150)
            pix.save(output_path)
            return True
        finally:
            doc.close()

    def pdf_to_text(self, input_path: str, output_path: str) -> bool:
        logger.info(f"Extracting text from PDF")
        doc = fitz.open(input_path)
        try:
            full_text = []
            for page in doc:
                full_text.append(page.get_text())
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n--- Page Break ---\n\n".join(full_text))
            return True
        finally:
            doc.close()

    def pdf_to_docx(self, input_path: str, output_path: str) -> bool:
        logger.info(f"Converting PDF to Word DOCX")
        from pdf2docx import Converter
        cv = Converter(input_path)
        try:
            cv.convert(output_path, start=0, end=None)
            return True
        finally:
            cv.close()
