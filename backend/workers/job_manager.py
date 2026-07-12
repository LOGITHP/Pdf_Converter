import uuid
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("job_manager")

class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Thread-safe Singleton
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JobManager, cls).__new__(cls)
                cls._instance.jobs = {}
                cls._instance.executor = ThreadPoolExecutor(max_workers=4)
        return cls._instance

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "result_file": None,
            "error": None,
            "engine": None
        }
        return job_id

    def update_job(self, job_id: str, status: str = None, progress: int = None, result_file: str = None, error: str = None, engine: str = None):
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        if status:
            job["status"] = status
        if progress is not None:
            job["progress"] = progress
        if result_file:
            job["result_file"] = result_file
        if error:
            job["error"] = error
        if engine:
            job["engine"] = engine

    def get_job_status(self, job_id: str) -> dict:
        return self.jobs.get(job_id, {"status": "not_found", "progress": 0, "error": "Job not found"})

    def submit_task(self, job_id: str, func, *args, **kwargs):
        """Submit a conversion task to be executed in the background thread pool."""
        self.update_job(job_id, status="processing", progress=5)
        self.executor.submit(self._run_task_wrapper, job_id, func, *args, **kwargs)

    def _run_task_wrapper(self, job_id: str, func, *args, **kwargs):
        try:
            logger.info(f"Starting background job: {job_id}")
            self.update_job(job_id, progress=25)
            
            # Run the actual conversion function
            # The function should return (result_file, engine_name)
            result_file, engine = func(job_id, *args, **kwargs)
            
            self.update_job(
                job_id, 
                status="completed", 
                progress=100, 
                result_file=result_file, 
                engine=engine
            )
            logger.info(f"Background job completed successfully: {job_id}")
        except Exception as e:
            logger.error(f"Error in background job {job_id}: {e}", exc_info=True)
            self.update_job(
                job_id, 
                status="failed", 
                progress=0, 
                error=str(e)
            )
