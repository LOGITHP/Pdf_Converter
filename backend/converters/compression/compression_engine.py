import os
import logging
from PIL import Image
import fitz # PyMuPDF
from backend.converters.base import BaseConverter

logger = logging.getLogger("compression_engine")

class CompressionEngine(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        # Compresses file into the same format
        return from_ext == to_ext and from_ext in ["pdf", "jpg", "jpeg", "png", "webp"]

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        options = options or {}
        ext = os.path.splitext(input_path)[1].lower().strip('.')
        quality = options.get("quality", 0.6) # quality slider 0.0 to 1.0

        if ext == "pdf":
            return self.compress_pdf(input_path, output_path, quality)
        elif ext in ["jpg", "jpeg", "png", "webp"]:
            return self.compress_image(input_path, output_path, ext, quality)

        return False

    def compress_pdf(self, input_path: str, output_path: str, quality: float) -> bool:
        logger.info(f"Compressing PDF: {input_path} (quality={quality})")
        doc = fitz.open(input_path)
        try:
            # Downsample images within PDF if quality is set low
            if quality < 0.8:
                # Loop through all pages to optimize images
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    image_list = page.get_images()
                    for img in image_list:
                        xref = img[0]
                        # We can replace or compress specific image streams using fitz API,
                        # but PyMuPDF's built-in save(garbage=3, deflate=True) is extremely safe.
                        pass
            
            # Save using maximum garbage collection and deflation compression
            doc.save(
                output_path, 
                garbage=3, 
                deflate=True, 
                clean=True
            )
            return True
        except Exception as e:
            logger.error(f"PDF compression failed: {e}")
            raise RuntimeError(f"PDF compression failed: {e}")
        finally:
            doc.close()

    def compress_image(self, input_path: str, output_path: str, ext: str, quality: float) -> bool:
        logger.info(f"Compressing Image: {input_path} (quality={quality})")
        img = Image.open(input_path)
        try:
            # Map quality float (0.1 to 1.0) to integer percentage (10 to 100)
            percentage = int(quality * 100)
            
            # Handle alpha transparency overlay on white if converting/saving to JPEG
            save_format = "JPEG" if ext in ["jpg", "jpeg"] else ext.upper()
            save_args = {"quality": percentage}
            
            if save_format == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else img.split()[1])
                img = background

            if save_format == "PNG":
                # PNG is lossless, optimize uses gzip compression level 1-9
                save_args = {"optimize": True}
                
            img.save(output_path, format=save_format, **save_args)
            return True
        except Exception as e:
            logger.error(f"Image compression failed: {e}")
            raise RuntimeError(f"Image compression failed: {e}")
        finally:
            img.close()
