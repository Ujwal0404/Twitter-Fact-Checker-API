from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime

from .config import get_settings
from .utils.logging import setup_logging, get_logger
from .api.routes import router
from .api.dependencies import check_results

settings = get_settings()
setup_logging()
logger = get_logger("fact_checker.main")

app = FastAPI(
    title=settings.APP_NAME,
    description="API for fact-checking tweets and text statements",
    version="1.0.0",
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def setup_cleanup():
    async def cleanup_old_results():
        logger.info("Starting cleanup task")
        while True:
            try:
                current_time = datetime.utcnow()
                for check_id in list(check_results.keys()):
                    check = check_results[check_id]
                    if check["status"] in ["completed", "failed"]:
                        completed_at = check["completed_at"]
                        if completed_at and (current_time - completed_at).total_seconds() > settings.CACHE_TTL:
                            del check_results[check_id]
                            logger.debug(f"Cleaned up check {check_id}")
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)

    asyncio.create_task(cleanup_old_results())
    logger.info("Cleanup task initialized")

# run.py
import uvicorn
from app.utils.logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)