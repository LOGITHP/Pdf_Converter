import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from backend.utils.sys_info import get_system_diagnostics
from backend.router.router import ConversionRouter
from backend.workers.job_manager import JobManager
from backend.utils.cleanup import TEMP_DIR, OUTPUT_DIR, ensure_directories

logger = logging.getLogger("api_endpoints")
router = APIRouter()
job_manager = JobManager()
conversion_router = ConversionRouter()

ensure_directories()

@router.get("/api/status")
def get_status():
    """Returns the diagnostics of converter engines on the server."""
    try:
        return get_system_diagnostics()
    except Exception as e:
        logger.error(f"Failed to get diagnostics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    """Poll the status/progress of a background conversion task."""
    status = job_manager.get_job_status(job_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@router.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    to_ext: str = Form(...),
    ocr: bool = Form(False)
):
    """
    Submits a file for conversion. Returns a job ID to track progress.
    """
    from_ext = os.path.splitext(file.filename)[1].lower().strip('.')
    to_ext = to_ext.lower().strip('.')

    supported = False
    for conv in conversion_router.converters:
        if conv.can_convert(from_ext, to_ext):
            supported = True
            break
            
    if not supported:
        raise HTTPException(
            status_code=400, 
            detail=f"Direct conversion path from .{from_ext} to .{to_ext} is not supported."
        )

    temp_input_name = f"input_{uuid_prefix()}_{file.filename}"
    temp_input_path = os.path.join(TEMP_DIR, temp_input_name)
    
    try:
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    job_id = job_manager.create_job()
    
    output_filename = f"converted_{uuid_prefix()}_{os.path.splitext(file.filename)[0]}.{to_ext}"
    temp_output_path = os.path.join(OUTPUT_DIR, output_filename)

    def run_conversion(jid):
        try:
            engine_name = conversion_router.convert_file(
                temp_input_path, 
                temp_output_path, 
                {"ocr": ocr}
            )
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            return output_filename, engine_name
        except Exception as err:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            raise err

    job_manager.submit_task(job_id, run_conversion)
    return {"job_id": job_id, "status": "queued"}

@router.post("/api/compress")
async def compress_file(
    file: UploadFile = File(...),
    quality: float = Form(0.6)
):
    """
    Submits a PDF or image for compression. Returns job ID.
    """
    from_ext = os.path.splitext(file.filename)[1].lower().strip('.')
    if from_ext not in ["pdf", "jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only PDF and image files are supported for compression.")

    temp_input_name = f"compress_input_{uuid_prefix()}_{file.filename}"
    temp_input_path = os.path.join(TEMP_DIR, temp_input_name)
    
    try:
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file for compression: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file.")

    job_id = job_manager.create_job()
    
    output_filename = f"compressed_{uuid_prefix()}_{file.filename}"
    temp_output_path = os.path.join(OUTPUT_DIR, output_filename)

    def run_compression(jid):
        try:
            engine_name = conversion_router.convert_file(
                temp_input_path, 
                temp_output_path, 
                {"operation": "compress", "quality": quality}
            )
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            return output_filename, engine_name
        except Exception as err:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            raise err

    job_manager.submit_task(job_id, run_compression)
    return {"job_id": job_id, "status": "queued"}

@router.post("/api/pdf/merge")
async def pdf_merge(
    files: list[UploadFile] = File(...)
):
    """
    Merges multiple uploaded PDF documents. Returns job ID.
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least 2 PDF files to merge.")

    temp_paths = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="All files submitted to merge must be PDFs.")
        
        tpath = os.path.join(TEMP_DIR, f"merge_in_{uuid_prefix()}_{file.filename}")
        try:
            with open(tpath, "wb") as buf:
                shutil.copyfileobj(file.file, buf)
            temp_paths.append(tpath)
        except Exception as e:
            logger.error(f"Error saving file for merge: {e}")
            raise HTTPException(status_code=500, detail="Error uploading files.")

    job_id = job_manager.create_job()
    output_filename = f"merged_{uuid_prefix()}_document.pdf"
    temp_output_path = os.path.join(OUTPUT_DIR, output_filename)

    def run_merge(jid):
        try:
            # Get the PDF Converter engine directly from router
            from backend.converters.pdf.pdf_converter import PDFConverter
            conv = PDFConverter()
            conv.merge_pdfs(temp_paths, temp_output_path)
            
            # Clean up temp inputs
            for tp in temp_paths:
                if os.path.exists(tp):
                    os.remove(tp)
            return output_filename, "PyMuPDF Merger"
        except Exception as err:
            for tp in temp_paths:
                if os.path.exists(tp):
                    os.remove(tp)
            raise err

    job_manager.submit_task(job_id, run_merge)
    return {"job_id": job_id, "status": "queued"}

@router.post("/api/pdf/edit")
async def pdf_edit(
    file: UploadFile = File(...),
    operation: str = Form(...),
    watermark_text: str = Form(None),
    password: str = Form(None),
    rotation_angle: int = Form(None)
):
    """
    Executes a single file PDF editing action: split, rotate, watermark, encrypt, decrypt.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    temp_input_name = f"edit_in_{uuid_prefix()}_{file.filename}"
    temp_input_path = os.path.join(TEMP_DIR, temp_input_name)
    try:
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file for editing: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file.")

    job_id = job_manager.create_job()
    
    # Reroute options
    options = {
        "operation": operation,
        "watermark_text": watermark_text,
        "password": password,
        "rotation_angle": rotation_angle
    }

    output_filename = f"edited_{uuid_prefix()}_{operation}_{file.filename}"
    temp_output_path = os.path.join(OUTPUT_DIR, output_filename)

    def run_edit(jid):
        try:
            # We want to support 'split' returning a ZIP folder of pages!
            # Let's check if the operation is split
            from backend.converters.pdf.pdf_converter import PDFConverter
            conv = PDFConverter()
            
            if operation == "split":
                # Splitting outputs multiple files. Let's zip them!
                split_dir = os.path.join(TEMP_DIR, f"split_{uuid_prefix()}")
                os.makedirs(split_dir, exist_ok=True)
                generated_pages = conv.split_pdf(temp_input_path, split_dir)
                
                # Create a zip file of split_dir and save it to temp_output_path
                zip_filename = f"split_pages_{uuid_prefix()}.zip"
                zip_output_path = os.path.join(OUTPUT_DIR, zip_filename)
                
                import zipfile
                with zipfile.ZipFile(zip_output_path, 'w') as zipf:
                    for fpage in generated_pages:
                        zipf.write(fpage, os.path.basename(fpage))
                        
                # Clean up split dir and temp pages
                shutil.rmtree(split_dir)
                if os.path.exists(temp_input_path):
                    os.remove(temp_input_path)
                return zip_filename, "PyMuPDF Splitter"

            # Other standard operations (rotate, watermark, encrypt, decrypt)
            engine_name = conversion_router.convert_file(
                temp_input_path, 
                temp_output_path, 
                options
            )
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            return output_filename, engine_name
        except Exception as err:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            raise err

    job_manager.submit_task(job_id, run_edit)
    return {"job_id": job_id, "status": "queued"}

from starlette.background import BackgroundTask

@router.get("/api/download/{filename}")
def download_file(filename: str):
    """Download a completed conversion/compression output file."""
    clean_filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, clean_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or expired.")
        
    return FileResponse(
        file_path, 
        media_type="application/octet-stream", 
        filename=clean_filename.split('_', 2)[-1],
        background=BackgroundTask(os.remove, file_path)
    )

def uuid_prefix():
    import uuid
    return uuid.uuid4().hex[:8]
