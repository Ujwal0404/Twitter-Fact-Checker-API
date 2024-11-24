from typing import Dict
from fastapi import Depends
from ..config import get_settings, Settings
from ..services.fact_checker import FactCheckManager
from ..utils.logging import get_logger

logger = get_logger("fact_checker.api.dependencies")
fact_checker = FactCheckManager()
check_results: Dict = {}

async def get_settings_dependency():
    return get_settings()

async def get_fact_checker():
    return fact_checker

async def get_check_results():
    return check_results