# app/core/workflow.py

from typing import Dict, TypedDict, List, Optional, Any, Callable
from langgraph.graph import StateGraph, END
from .search import MultiSearchTool
from .analysis import GroqTool
from ..utils.logging import get_logger

logger = get_logger("fact_checker.core.workflow")

class State(TypedDict):
    text: str
    tweet_data: Optional[Dict]
    search_results: List[Dict]
    evaluated_sources: List[Dict]
    analysis: Dict
    response: List[str]
    error: str
    context: Dict
    config: Dict

class FactCheckWorkflow:
    def __init__(self):
        self.searcher = MultiSearchTool()
        self.groq = GroqTool()
        logger.info("FactCheckWorkflow initialized")

    def start(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            config = state["config"]
            tweet_id = config.get('tweet_id')

            if tweet_id:
                tweet_data = self.searcher.get_tweet_data(tweet_id)
                if not tweet_data:
                    return {**state, "error": f"Could not fetch tweet with ID {tweet_id}"}

                return {
                    **state,
                    "text": tweet_data['text'],
                    "tweet_data": tweet_data,
                    "context": self.searcher.get_additional_context(tweet_data['text'], tweet_data)
                }
            else:
                text = config.get('text')
                if not text:
                    return {**state, "error": "No text or tweet ID provided"}

                return {
                    **state,
                    "text": text,
                    "context": self.searcher.get_additional_context(text)
                }

        except Exception as e:
            logger.error(f"Error in start: {str(e)}")
            return {**state, "error": f"Error in start: {str(e)}"}

    def search(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("error"):
            return state

        try:
            search_results = self.searcher.search(
                state["text"],
                state.get("tweet_data")
            )

            if not search_results:
                return {**state, "error": "No sources found"}

            return {**state, "search_results": search_results}

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {**state, "error": f"Search error: {str(e)}"}

    def evaluate_and_analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("error"):
            return state

        try:
            evaluated_sources = self.groq.evaluate_sources(
                state["text"],
                state["search_results"],
                state.get("tweet_data")
            )

            analysis = self.groq.analyze_claim(
                state["text"],
                evaluated_sources,
                state.get("tweet_data")
            )

            return {
                **state,
                "evaluated_sources": evaluated_sources,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {**state, "error": f"Analysis error: {str(e)}"}

    def format_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("error"):
            return state

        try:
            analysis = state["analysis"]
            responses = []

            if state.get("tweet_data"):
                tweet_data = state["tweet_data"]
                tweet_info = (
                    f"🐦 Tweet Information:\n"
                    f"Author: @{tweet_data['author_username']}\n"
                    f"Posted: {tweet_data['created_at']}\n"
                    f"Engagement: {tweet_data['metrics']['likes']} likes, "
                    f"{tweet_data['metrics']['retweets']} retweets, "
                    f"{tweet_data['metrics']['replies']} replies\n"
                    f"\nTweet Text: {tweet_data['text']}\n"
                )
                responses.append(tweet_info)

            main_result = (
                f"🔍 Fact Check Results\n"
                f"Verdict: {analysis['verdict']}\n"
                f"Confidence: {analysis['confidence']}\n\n"
                f"Summary: {analysis['fact_check_summary']['main_conclusion']}\n\n"
                f"Confidence Explanation: {analysis['fact_check_summary']['confidence_explanation']}"
            )
            responses.append(main_result)

            evidence_analysis = (
                f"📊 Evidence Analysis\n"
                f"Overall Quality: {analysis['evidence_quality']['overall_assessment']}\n"
                f"Strength: {analysis['evidence_quality']['strength_of_evidence']}\n"
                f"Consistency: {analysis['evidence_quality']['consistency_across_sources']}\n\n"
                f"Source Consensus: {analysis['source_consensus']['description']}\n\n"
                f"Supporting Evidence:\n" +
                "\n".join(f"• {evidence}" for evidence in analysis['supporting_evidence']) +
                "\n\nCounter Evidence:\n" +
                "\n".join(f"• {evidence}" for evidence in analysis['counter_evidence'])
            )
            responses.append(evidence_analysis)

            context_analysis = (
                f"📅 Temporal Analysis:\n"
                f"{analysis['temporal_analysis']['time_relevance']}\n"
                f"Recent Developments: {analysis['temporal_analysis']['recent_developments']}\n\n"
            )

            if state.get("tweet_data"):
                context_analysis += (
                    f"👥 Social Context:\n"
                    f"Virality: {analysis['social_context']['virality']}\n"
                    f"Community Response: {analysis['social_context']['community_response']}\n"
                )

            responses.append(context_analysis)

            sources = (
                "📚 Sources Analysis:\n" +
                "\n".join([
                    f"• {s['source_type']}: {s['url']}\n"
                    f"  Reliability: {s['reliability_score']}, "
                    f"Relevance: {s['relevance_score']}\n"
                    f"  Engine: {s['search_engine']}"
                    for s in state['evaluated_sources']
                    if s.get('use_for_analysis', True)
                ])
            )
            responses.append(sources)

            limitations = (
                "⚠️ Limitations & Key Considerations:\n" +
                "\n".join(f"• {limitation}" for limitation in analysis['limitations']) +
                "\n\nKey Considerations:\n" +
                "\n".join(f"• {consideration}" for consideration in analysis['fact_check_summary']['key_considerations'])
            )
            responses.append(limitations)

            return {**state, "response": responses}

        except Exception as e:
            logger.error(f"Formatting error: {str(e)}")
            return {**state, "error": f"Formatting error: {str(e)}"}

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the fact-checking workflow"""
        try:
            # Start step
            state = self.start(state)
            if state.get("error"):
                return state

            # Search step
            state = self.search(state)
            if state.get("error"):
                return state

            # Evaluate and analyze step
            state = self.evaluate_and_analyze(state)
            if state.get("error"):
                return state

            # Format response step
            state = self.format_response(state)
            return state

        except Exception as e:
            logger.error(f"Error in workflow process: {str(e)}")
            return {**state, "error": f"Workflow process error: {str(e)}"}

def create_fact_check_graph() -> FactCheckWorkflow:
    """Create and return a fact-checking workflow instance"""
    return FactCheckWorkflow()