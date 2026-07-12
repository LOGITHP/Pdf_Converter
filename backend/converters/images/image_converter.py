import os
import logging
from PIL import Image
from backend.converters.base import BaseConverter

logger = logging.getLogger("image_converter")

# Optional HEIC support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_AVAILABLE = True
except ImportError:
    HEIC_AVAILABLE = False

class ImageConverter(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        supported = ["png", "jpg", "jpeg", "bmp", "tiff", "gif", "webp", "pdf", "ico"]
        if HEIC_AVAILABLE:
            supported.append("heic")
            
        if from_ext in supported:
            return to_ext in supported
        return False

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')
        options = options or {}
        
        if from_ext == "heic" and not HEIC_AVAILABLE:
            raise ImportError(
                "HEIC image format support requires 'pillow-heif' python package. "
                "Please run: pip install pillow-heif"
            )

        logger.info(f"Converting image: {input_path} -> {output_path}")
        
        # Load image
        img = Image.open(input_path)
        
        try:
            # Preserve original EXIF metadata if requested
            if options.get("preserve_metadata", True) and "exif" in img.info:
                exif = img.info["exif"]
            else:
                exif = None

            # Apply manipulations: resize
            if "resize_width" in options or "resize_height" in options:
                w, h = img.size
                target_w = options.get("resize_width", w)
                target_h = options.get("resize_height", h)
                img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Apply manipulations: rotate
            if "rotate_angle" in options:
                # Options: 90, 180, 270 (counter-clockwise)
                angle = options.get("rotate_angle", 0)
                if angle:
                    img = img.rotate(angle, expand=True)

            # Apply manipulations: crop
            if "crop" in options:
                # crop options format: [left, top, right, bottom]
                crop_box = options.get("crop")
                if len(crop_box) == 4:
                    img = img.crop(crop_box)

            # Handle Transparency for PDF and JPEG which do not support alpha channel
            if to_ext in ["pdf", "jpg", "jpeg"] and img.mode in ("RGBA", "LA", "P"):
                # Overlay transparent image on white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    # Convert palette image to RGBA first
                    img = img.convert("RGBA")
                # Paste alpha mask
                background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else img.split()[1])
                img = background

            # Save options
            save_args = {}
            if exif:
                save_args["exif"] = exif
                
            if to_ext in ["jpg", "jpeg", "webp"]:
                # Compression quality
                quality = int(options.get("quality", 80))
                save_args["quality"] = quality
            elif to_ext == "pdf":
                save_args["resolution"] = 100.0

            img.save(output_path, **save_args)
            return True
        finally:
            img.close()
