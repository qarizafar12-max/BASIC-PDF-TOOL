import os
from typing import List, Dict, Callable, Any, Tuple
from enum import Enum
from PySide6.QtCore import QObject, Signal, QThread


class BatchOperationType(Enum):
    """Types of batch operations."""
    MERGE = "merge"
    SPLIT = "split"
    COMPRESS = "compress"
    EXTRACT_TEXT = "extract_text"
    ROTATE = "rotate"
    PASSWORD_ADD = "add_password"
    PASSWORD_REMOVE = "remove_password"


class BatchJob:
    """Represents a single batch job."""
    
    def __init__(self, operation_type: BatchOperationType, input_files: List[str], 
                 output_path: str, params: Dict[str, Any] = None):
        """
        Initialize batch job.
        
        Args:
            operation_type: Type of operation
            input_files: List of input file paths
            output_path: Output file/directory path
            params: Additional parameters for the operation
        """
        self.operation_type = operation_type
        self.input_files = input_files
        self.output_path = output_path
        self.params = params or {}
        self.status = "pending"
        self.result = None
        self.error = None


class BatchProcessor(QObject):
    """Handles batch processing of PDF operations."""
    
    # Signals for progress updates
    job_started = Signal(int)  # job_index
    job_completed = Signal(int, bool, str)  # job_index, success, message
    batch_completed = Signal()
    
    def __init__(self):
        super().__init__()
        self.jobs: List[BatchJob] = []
        self.current_job_index = 0
        self.is_running = False
    
    def add_job(self, job: BatchJob):
        """Add a job to the batch queue."""
        self.jobs.append(job)
    
    def clear_jobs(self):
        """Clear all jobs from the queue."""
        self.jobs.clear()
        self.current_job_index = 0
    
    def remove_job(self, index: int):
        """Remove a job from the queue by index."""
        if 0 <= index < len(self.jobs):
            self.jobs.pop(index)
            if self.current_job_index >= index and self.current_job_index > 0:
                self.current_job_index -= 1
    
    def process_batch(self, processor_func: Callable):
        """
        Process all jobs in the batch.
        
        Args:
            processor_func: Function to call for processing each job
        """
        self.is_running = True
        
        for i, job in enumerate(self.jobs):
            if not self.is_running:
                break
            
            self.current_job_index = i
            self.job_started.emit(i)
            
            try:
                # Call processor function with job details
                success, message = processor_func(job)
                job.status = "completed" if success else "failed"
                job.result = message
                self.job_completed.emit(i, success, message)
            except Exception as e:
                job.status = "failed"
                job.error = str(e)
                self.job_completed.emit(i, False, str(e))
        
        self.is_running = False
        self.batch_completed.emit()
    
    def stop(self):
        """Stop batch processing."""
        self.is_running = False
    
    def get_job_count(self) -> int:
        """Get total number of jobs."""
        return len(self.jobs)
    
    def get_pending_count(self) -> int:
        """Get number of pending jobs."""
        return len([j for j in self.jobs if j.status == "pending"])
    
    def get_completed_count(self) -> int:
        """Get number of completed jobs."""
        return len([j for j in self.jobs if j.status == "completed"])
    
    def get_failed_count(self) -> int:
        """Get number of failed jobs."""
        return len([j for j in self.jobs if j.status == "failed"])
