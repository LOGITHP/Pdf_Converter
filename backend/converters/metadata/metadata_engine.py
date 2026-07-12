import os
import logging
import fitz # PyMuPDF
from PIL import Image
from backend.converters.base import BaseConverter

logger = logging.getLogger("metadata_engine")

class MetadataEngine(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        # It doesn't convert, it reads/writes metadata for the same extension
        return from_ext.lower().strip('.') == to_ext.lower().strip('.')

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        # Just copy file, modify metadata on output_path
        import shutil
        shutil.copy2(input_path, output_path)
        
        options = options or {}
        metadata = options.get("metadata", {})
        if not metadata:
            return True

        ext = os.path.splitext(output_path)[1].lower().strip('.')
        if ext == "pdf":
            return self.write_pdf_metadata(output_path, metadata)
        elif ext in ["jpg", "jpeg", "png"]:
            return self.write_image_metadata(output_path, metadata)

        return True

    def read_metadata(self, file_path: str) -> dict:
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        if ext == "pdf":
            return self.read_pdf_metadata(file_path)
        elif ext in ["jpg", "jpeg", "png"]:
            return self.read_image_metadata(file_path)
        return {}

    def read_pdf_metadata(self, file_path: str) -> dict:
        doc = fitz.open(file_path)
        try:
            meta = doc.metadata
            return {
                "title": meta.get("title", ""),
                "author": meta.get("author", ""),
                "subject": meta.get("subject", ""),
                "keywords": meta.get("keywords", ""),
                "creator": meta.get("creator", ""),
                "producer": meta.get("producer", ""),
                "creationDate": meta.get("creationDate", ""),
                "modDate": meta.get("modDate", "")
            }
        finally:
            doc.close()

    def write_pdf_metadata(self, file_path: str, metadata_to_write: dict) -> bool:
        doc = fitz.open(file_path)
        try:
            # Get current metadata, update with keys
            meta = doc.metadata or {}
            for k, v in metadata_to_write.items():
                meta[k] = v
            doc.set_metadata(meta)
            # Save incremental updates
            doc.save(file_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            return True
        except Exception as e:
            logger.error(f"Failed to write PDF metadata: {e}")
            return False
        finally:
            doc.close()

    def read_image_metadata(self, file_path: str) -> dict:
        img = Image.open(file_path)
        try:
            info = img.info
            meta = {}
            # Check basic tags
            for key in ["title", "author", "description", "copyright"]:
                if key in info:
                    meta[key] = info[key]
            # Exif metadata
            exif = img.getexif()
            if exif:
                # Add basic EXIF info mapping
                # Tag 270 = ImageDescription, Tag 315 = Artist, Tag 33432 = Copyright
                if 270 in exif: meta["description"] = exif[270]
                if 315 in exif: meta["author"] = exif[315]
                if 33432 in exif: meta["copyright"] = exif[33432]
            return meta
        finally:
            img.close()

    def write_image_metadata(self, file_path: str, metadata_to_write: dict) -> bool:
        # Pillow can inject text comments into PNG, JPEG metadata info
        img = Image.open(file_path)
        try:
            info = img.info or {}
            # Update key values
            for k, v in metadata_to_write.items():
                info[k] = v
                
            # If JPEG, we can write EXIF
            exif = img.getexif()
            if 270 in exif or "description" in metadata_to_write:
                exif[270] = metadata_to_write.get("description", metadata_to_write.get("title", ""))
            if 315 in exif or "author" in metadata_to_write:
                exif[315] = metadata_to_write.get("author", "")
            if 33432 in exif or "copyright" in metadata_to_write:
                exif[33432] = metadata_to_write.get("copyright", "")
                
            # Overwrite image with new metadata
            img.save(file_path, exif=exif, **info)
            return True
        except Exception as e:
            logger.error(f"Failed to write image metadata: {e}")
            return False
        finally:
            img.close()
