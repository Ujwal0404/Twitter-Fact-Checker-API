from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from datetime import datetime

class TextCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    background_check: bool = Field(default=False, description="Run check in background")

    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace')
        return v.strip()

class TweetCheckRequest(BaseModel):
    tweet_id: str = Field(..., pattern="^[0-9]+$")
    background_check: bool = Field(default=False, description="Run check in background")

class CheckResponse(BaseModel):
    check_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None
    error: Optional[str] = None

class Source(BaseModel):
    url: str
    title: str
    snippet: str
    reliability_score: float
    relevance_score: float
    source_type: str
    reasoning: str
    potential_bias: str
    temporal_relevance: str
    search_engine: str

class Analysis(BaseModel):
    verdict: str
    confidence: str
    explanation: str
    key_points: List[str]
    evidence_quality: Dict
    source_consensus: Dict
    limitations: List[str]
    supporting_evidence: List[str]
    counter_evidence: List[str]
    temporal_analysis: Dict
    social_context: Dict
    fact_check_summary: Dict

