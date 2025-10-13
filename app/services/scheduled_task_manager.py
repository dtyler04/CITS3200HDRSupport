"""
Scheduled Task Manager
Handles scheduling and execution of recurring tasks like weekly digest emails.
"""

import logging
import schedule
import time
import threading
from datetime import datetime
from app.services.weekly_digest_service import WeeklyDigestService

class ScheduledTaskManager:
    """Manages scheduled tasks for the application."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weekly_digest_service = WeeklyDigestService()
        self.is_running = False
        self.scheduler_thread = None
    
    def setup_schedules(self):
        """Set up all scheduled tasks."""
        # Schedule weekly digest to run every Monday at 9:00 AM
        schedule.every().monday.at("09:00").do(self._run_weekly_digest)
        
        # For testing - uncomment to run every minute
        # schedule.every().minute.do(self._run_weekly_digest)
        
        self.logger.info("Scheduled tasks configured")
    
    def _run_weekly_digest(self):
        """Execute the weekly digest task with error handling."""
        try:
            self.logger.info("Starting weekly digest batch")
            start_time = datetime.now()
            
            result = self.weekly_digest_service.send_weekly_digests()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(
                f"Weekly digest batch completed in {duration:.2f} seconds. "
                f"Sent: {result['sent']}, Errors: {result['errors']}"
            )
            
        except Exception as e:
            self.logger.error(f"Weekly digest task failed: {e}")
    
    def start_scheduler(self):
        """Start the scheduler in a background thread."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.setup_schedules()
        self.is_running = True
        
        def run_scheduler():
            self.logger.info("Scheduler started")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Scheduler error: {e}")
                    time.sleep(60)  # Continue even if there's an error
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler thread started")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Scheduler stopped")
    
    def get_schedule_info(self):
        """Get information about scheduled jobs."""
        jobs_info = []
        for job in schedule.jobs:
            jobs_info.append({
                "job": str(job.job_func),
                "next_run": job.next_run,
                "interval": job.interval,
                "unit": job.unit
            })
        
        return {
            "is_running": self.is_running,
            "jobs": jobs_info
        }
    
    def run_weekly_digest_now(self):
        """Manually trigger the weekly digest (for testing/admin use)."""
        try:
            self.logger.info("Manually triggering weekly digest")
            return self.weekly_digest_service.send_weekly_digests()
        except Exception as e:
            self.logger.error(f"Manual weekly digest failed: {e}")
            raise

# Global instance
task_manager = ScheduledTaskManager()