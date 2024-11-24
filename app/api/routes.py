from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Dict
from uuid import uuid4
from datetime import datetime

from .models import TextCheckRequest, TweetCheckRequest, CheckResponse
from .dependencies import get_fact_checker, get_check_results
from ..utils.logging import get_logger
from ..services.fact_checker import FactCheckManager

logger = get_logger("fact_checker.api.routes")
router = APIRouter()

@router.post("/check/text", response_model=CheckResponse)
async def check_text(
    request: TextCheckRequest,
    background_tasks: BackgroundTasks,
    fact_checker: FactCheckManager = Depends(get_fact_checker),
    check_results: Dict = Depends(get_check_results)
):
    check_id = str(uuid4())
    logger.info(f"Starting text check {check_id}")
    
    check_results[check_id] = {
        "check_id": check_id,
        "status": "pending",
        "started_at": datetime.utcnow()
    }

    config = {"text": request.text}

    try:
        if request.background_check:
            background_tasks.add_task(
                fact_checker.run_check,
                check_id,
                config,
                check_results
            )
            logger.info(f"Background check {check_id} initiated")
        else:
            await fact_checker.run_check(check_id, config, check_results)
            logger.info(f"Synchronous check {check_id} completed")

        return CheckResponse(**check_results[check_id])
    except Exception as e:
        logger.error(f"Error in check_text {check_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/tweet", response_model=CheckResponse)
async def check_tweet(
    request: TweetCheckRequest,
    background_tasks: BackgroundTasks,
    fact_checker: FactCheckManager = Depends(get_fact_checker),
    check_results: Dict = Depends(get_check_results)
):
    check_id = str(uuid4())
    logger.info(f"Starting tweet check {check_id} for tweet {request.tweet_id}")
    
    check_results[check_id] = {
        "check_id": check_id,
        "status": "pending",
        "started_at": datetime.utcnow()
    }

    config = {"tweet_id": request.tweet_id}

    try:
        if request.background_check:
            background_tasks.add_task(
                fact_checker.run_check,
                check_id,
                config,
                check_results
            )
            logger.info(f"Background check {check_id} initiated")
        else:
            await fact_checker.run_check(check_id, config, check_results)
            logger.info(f"Synchronous check {check_id} completed")

        return CheckResponse(**check_results[check_id])
    except Exception as e:
        logger.error(f"Error in check_tweet {check_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check/{check_id}", response_model=CheckResponse)
async def get_check_status(
    check_id: str,
    check_results: Dict = Depends(get_check_results)
):
    logger.info(f"Fetching status for check {check_id}")
    if check_id not in check_results:
        logger.warning(f"Check {check_id} not found")
        raise HTTPException(status_code=404, detail="Check not found")
    
    return CheckResponse(**check_results[check_id])