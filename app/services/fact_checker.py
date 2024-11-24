# app/services/fact_checker.py

from typing import Dict, Optional, Any
from datetime import datetime
import asyncio
from ..core.workflow import create_fact_check_graph
from ..config import get_settings
from ..utils.logging import get_logger

settings = get_settings()
logger = get_logger("fact_checker.services.fact_checker")

class FactCheckManager:
    def __init__(self):
        """Initialize the FactCheckManager with the workflow"""
        try:
            self.workflow = create_fact_check_graph()
            logger.info("FactCheckManager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing FactCheckManager: {str(e)}")
            raise

    async def run_check(self, check_id: str, config: Dict[str, Any], check_results: Dict[str, Any]):
        """Run a fact check workflow"""
        try:
            logger.info(f"Starting fact check {check_id}")
            
            # Initialize state
            initial_state = {
                "text": "",
                "tweet_data": None,
                "search_results": [],
                "evaluated_sources": [],
                "analysis": {},
                "response": [],
                "error": "",
                "context": {},
                "config": config
            }

            # Run the workflow in a separate thread
            logger.debug(f"Running workflow for check {check_id}")
            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(
                None,
                self.workflow.process,
                initial_state
            )

            # Update check results
            if final_state.get("error"):
                logger.error(f"Error in fact check {check_id}: {final_state['error']}")
                check_results[check_id].update({
                    "status": "failed",
                    "completed_at": datetime.utcnow(),
                    "error": final_state["error"]
                })
            else:
                logger.info(f"Completed fact check {check_id}")
                check_results[check_id].update({
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "results": {
                        "responses": final_state.get("response", []),
                        "analysis": final_state.get("analysis", {}),
                        "evaluated_sources": final_state.get("evaluated_sources", []),
                        "context": final_state.get("context", {})
                    }
                })

        except Exception as e:
            logger.error(f"Unexpected error in fact check {check_id}: {str(e)}")
            check_results[check_id].update({
                "status": "failed",
                "completed_at": datetime.utcnow(),
                "error": f"Unexpected error: {str(e)}"
            })

    async def get_check_status(self, check_id: str, check_results: Dict) -> Optional[Dict]:
        """Get the status of a fact check"""
        try:
            logger.debug(f"Retrieving status for check {check_id}")
            return check_results.get(check_id)
        except Exception as e:
            logger.error(f"Error retrieving check status for {check_id}: {str(e)}")
            return None

    async def cleanup_old_checks(self, check_results: Dict, max_age: int = None):
        """Clean up old check results"""
        try:
            max_age = max_age or settings.CACHE_TTL
            current_time = datetime.utcnow()
            
            logger.info("Starting cleanup of old check results")
            initial_count = len(check_results)
            
            for check_id in list(check_results.keys()):
                check = check_results[check_id]
                if check["status"] in ["completed", "failed"]:
                    completed_at = check.get("completed_at")
                    if completed_at and (current_time - completed_at).total_seconds() > max_age:
                        del check_results[check_id]
                        logger.debug(f"Cleaned up check {check_id}")
            
            final_count = len(check_results)
            logger.info(f"Cleanup completed. Removed {initial_count - final_count} old results")
                        
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def __str__(self):
        return f"FactCheckManager(workflow_initialized={bool(self.workflow)})"