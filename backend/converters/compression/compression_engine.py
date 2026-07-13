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
        
        # Try to use Ghostscript for real PDF downsampling
        from backend.utils.sys_info import get_engine_path
        import subprocess
        
        gs_path = get_engine_path("ghostscript")
        if gs_path:
            try:
                gs_args = [
                    gs_path,
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                ]
                
                # Map our 0.0-1.0 quality slider to GS profiles
                if quality <= 0.4:
                    gs_args.append("-dPDFSETTINGS=/screen") # Lowest quality, smallest size (72dpi)
                elif quality <= 0.7:
                    gs_args.append("-dPDFSETTINGS=/ebook") # Medium quality (150dpi)
                else:
                    gs_args.append("-dPDFSETTINGS=/printer") # High quality (300dpi)
                    
                gs_args.extend([
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    f"-sOutputFile={output_path}",
                    input_path
                ])
                
                subprocess.run(gs_args, check=True, capture_output=True)
                return True
            except Exception as e:
                logger.warning(f"Ghostscript compression failed, falling back to PyMuPDF. Error: {e}")
        
        # Fallback to PyMuPDF deflation
        doc = fitz.open(input_path)
        try:
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
