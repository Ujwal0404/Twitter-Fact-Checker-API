# app/core/analysis.py
from typing import Dict, List, Optional
from groq import Groq
import json
from .search import MultiSearchTool
from ..config import get_settings
from ..utils.logging import get_logger

settings = get_settings()
logger = get_logger("fact_checker.core.analysis")

DEFAULT_EVALUATION_RESULT = {
    "url": "",
    "reliability_score": 0.5,
    "relevance_score": 0.5,
    "reasoning": "Unable to evaluate source",
    "source_type": "unknown",
    "search_engine": "unknown",
    "use_for_analysis": False,
    "title": "",
    "snippet": "",
    "potential_bias": "Unknown",
    "temporal_relevance": "Unknown"
}

DEFAULT_ANALYSIS_RESULT = {
    "verdict": "Unverifiable",
    "confidence": "low",
    "explanation": "Unable to analyze claim due to processing error",
    "key_points": ["Analysis failed"],
    "evidence_quality": {
        "overall_assessment": "Unable to assess",
        "strength_of_evidence": "weak",
        "consistency_across_sources": "low"
    },
    "source_consensus": {
        "level": "low",
        "description": "Unable to determine consensus"
    },
    "limitations": ["Analysis failed"],
    "counter_evidence": [],
    "supporting_evidence": [],
    "temporal_analysis": {
        "time_relevance": "Unknown",
        "recent_developments": "Unable to determine"
    },
    "social_context": {
        "virality": "Unable to assess",
        "community_response": "Unable to determine"
    },
    "fact_check_summary": {
        "main_conclusion": "Analysis failed",
        "confidence_explanation": "Analysis error occurred",
        "key_considerations": ["Analysis failed to complete"]
    }
}

class GroqTool:
    def __init__(self):
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.search_tool = MultiSearchTool()
            logger.info("GroqTool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GroqTool: {str(e)}")
            raise

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for JSON"""
        if not isinstance(text, str):
            text = str(text)
        return text.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ').strip()

    def _safe_json_parse(self, content: str, default_value: any) -> any:
        """Safely parse JSON content"""
        try:
            # Remove any potential markdown formatting
            content = content.strip().strip('```json').strip('```').strip()
            
            # Try to parse the JSON
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            logger.error(f"Problematic content: {content[:500]}...")  # Log first 500 chars
            return default_value

    def evaluate_sources(self, query: str, sources: List[Dict], tweet_data: Optional[Dict] = None) -> List[Dict]:
        try:
            logger.info(f"Evaluating sources for query: {query}")
            context = self.search_tool.get_additional_context(query, tweet_data)

            # Prepare source data safely
            source_data = []
            for s in sources:
                source_data.append({
                    'title': self._sanitize_text(s.get('title', '')),
                    'snippet': self._sanitize_text(s.get('snippet', '')),
                    'url': self._sanitize_text(s.get('url', '')),
                    'domain': self._sanitize_text(s.get('domain', '')),
                    'engine': self._sanitize_text(s.get('engine', ''))
                })

            tweet_info = ""
            if tweet_data:
                tweet_info = {
                    'author': tweet_data['author_username'],
                    'created_at': str(tweet_data['created_at']),
                    'metrics': tweet_data['metrics']
                }

            evaluation_prompt = {
                'query': self._sanitize_text(query),
                'tweet_info': tweet_info,
                'wikipedia_context': context.get('wikipedia', {}).get('summary', ''),
                'sources': source_data
            }

            prompt = f"""
You are an expert source evaluator. Evaluate the provided sources and return ONLY a JSON object.

Input data: {json.dumps(evaluation_prompt, ensure_ascii=False)}

Return ONLY a JSON object in this exact format, with no additional text:
{{
    "evaluated_sources": [
        {{
            "url": "string",
            "reliability_score": number between 0 and 1,
            "relevance_score": number between 0 and 1,
            "reasoning": "string",
            "source_type": "string",
            "search_engine": "string",
            "use_for_analysis": boolean,
            "title": "string",
            "snippet": "string",
            "potential_bias": "string",
            "temporal_relevance": "string"
        }}
    ]
}}
"""

            logger.debug("Sending source evaluation request to Groq")
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a source evaluation expert. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.1,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            result = self._safe_json_parse(content, {"evaluated_sources": [DEFAULT_EVALUATION_RESULT]})
            logger.info(f"Successfully evaluated {len(result['evaluated_sources'])} sources")
            return result["evaluated_sources"]

        except Exception as e:
            logger.error(f"Source evaluation error: {str(e)}")
            return [DEFAULT_EVALUATION_RESULT]

    def analyze_claim(self, claim: str, evaluated_sources: List[Dict], tweet_data: Optional[Dict] = None) -> Dict:
        try:
            logger.info(f"Analyzing claim: {claim}")
            relevant_sources = [s for s in evaluated_sources if s.get("use_for_analysis", True)]
            
            # Prepare analysis data safely
            analysis_data = {
                'claim': self._sanitize_text(claim),
                'sources': [
                    {
                        'url': self._sanitize_text(s.get('url', '')),
                        'source_type': self._sanitize_text(s.get('source_type', '')),
                        'reliability_score': float(s.get('reliability_score', 0)),
                        'relevance_score': float(s.get('relevance_score', 0)),
                        'snippet': self._sanitize_text(s.get('snippet', '')),
                        'reasoning': self._sanitize_text(s.get('reasoning', '')),
                        'potential_bias': self._sanitize_text(s.get('potential_bias', ''))
                    }
                    for s in relevant_sources
                ]
            }

            if tweet_data:
                analysis_data['tweet_info'] = {
                    'author': tweet_data['author_username'],
                    'created_at': str(tweet_data['created_at']),
                    'metrics': tweet_data['metrics']
                }

            prompt = f"""
You are a fact-checker. Analyze the claim using the provided sources and return ONLY a JSON object.

Input data: {json.dumps(analysis_data, ensure_ascii=False)}

Return ONLY a JSON object in this exact format, with no additional text:
{{
    "verdict": "True|False|Partially True|Unverifiable",
    "confidence": "high|medium|low",
    "explanation": "string",
    "key_points": ["string"],
    "evidence_quality": {{
        "overall_assessment": "string",
        "strength_of_evidence": "strong|moderate|weak",
        "consistency_across_sources": "high|medium|low"
    }},
    "source_consensus": {{
        "level": "high|medium|low",
        "description": "string"
    }},
    "limitations": ["string"],
    "counter_evidence": ["string"],
    "supporting_evidence": ["string"],
    "temporal_analysis": {{
        "time_relevance": "string",
        "recent_developments": "string"
    }},
    "social_context": {{
        "virality": "string",
        "community_response": "string"
    }},
    "fact_check_summary": {{
        "main_conclusion": "string",
        "confidence_explanation": "string",
        "key_considerations": ["string"]
    }}
}}
"""

            logger.debug("Sending claim analysis request to Groq")
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fact-checker. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.1,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            result = self._safe_json_parse(content, DEFAULT_ANALYSIS_RESULT)
            logger.info(f"Claim analysis completed with verdict: {result.get('verdict', 'Unknown')}")
            return result

        except Exception as e:
            logger.error(f"Claim analysis error: {str(e)}")
            return DEFAULT_ANALYSIS_RESULT