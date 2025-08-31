"""
Extractor Agent Node - Query Parser
Refactored to use LangGraph properly.

Purpose: Parse free-text into a normalized request object
Inputs: User message, session context, consent object
Outputs: Structured RequestParsed object
"""

import json
import logging
from typing import Dict, Any, Optional, Annotated
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.models.state import GraphState, RequestParsed, TelemetryEvent
from src.tools.base import LLMTool, PolicyTool


logger = logging.getLogger(__name__)


def create_extractor_node(llm_tool: LLMTool, policy_tool: PolicyTool):
    """
    Create the Extractor node using LangGraph.
    
    Args:
        llm_tool: LLM tool for extraction
        policy_tool: Policy tool for validation
        
    Returns:
        Extractor node function
    """
    
    async def extractor_node(state: GraphState) -> GraphState:
        """
        Execute the Extractor node using LangGraph state management.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with parsed request
        """
        try:
            # Update current node tracking
            state.current_node = "extractor"
            
            # Extract inputs from state
            raw_text = state.user_query
            consent = state.consent
            locale = state.locale
            
            # Validate inputs
            if not raw_text:
                raise ValueError("No user query provided")
            
            # Parse using LLM tool
            parsed_request = await _extract_structured_data(llm_tool, raw_text, consent, locale)
            
            # Validate parsed request
            validated_request = await _validate_request(policy_tool, parsed_request, consent, locale)
            
            # Create telemetry event
            telemetry_event = TelemetryEvent(
                name="extractor.ok",
                metadata={"confidence": parsed_request.get("confidence", 0.0)}
            )
            
            # Update state
            state.request = validated_request
            state.telemetry["events"] = state.telemetry.get("events", []) + [telemetry_event.dict()]
            state.completed_nodes.append("extractor")
            state.next_nodes = ["router"]  # Next node in the flow
            
            logger.info(f"Extractor completed successfully for session {state.session_id}")
            return state
            
        except Exception as e:
            logger.error(f"Extractor failed: {str(e)}")
            # Add error to state
            state.errors.append({
                "node": "extractor",
                "error": str(e),
                "timestamp": str(TelemetryEvent().timestamp)
            })
            # Set next node to error handler
            state.next_nodes = ["error_handler"]
            raise
    
    return extractor_node


async def _extract_structured_data(llm_tool: LLMTool, text: str, consent: Any, locale: str) -> Dict[str, Any]:
    """
    Extract structured data from raw text using LLM.
    
    Args:
        llm_tool: LLM tool for extraction
        text: Raw user query
        consent: User consent object
        locale: User locale
        
    Returns:
        Parsed structured data
    """
    # Define extraction schema based on document specifications
    extraction_schema = {
        "type": "object",
        "properties": {
            "intent": {"type": "string", "enum": ["recommend_card"]},
            "constraints": {
                "type": "object",
                "properties": {
                    "annual_fee_max": {"type": "number", "minimum": 0},
                    "fx_fee_max_pct": {"type": "number", "minimum": 0, "maximum": 10},
                    "min_credit_score": {"type": "number", "minimum": 300, "maximum": 850}
                }
            },
            "goals": {
                "type": "array",
                "items": {"type": "string"},
                "enum": ["miles", "cashback", "rewards", "travel", "business", "student"]
            },
            "priority": {
                "type": "array",
                "items": {"type": "string"}
            },
            "spend_focus": {
                "type": "object",
                "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "jurisdiction": {"type": "string", "default": "SG"},
            "risk_tolerance": {
                "type": "string",
                "enum": ["conservative", "standard", "aggressive"],
                "default": "standard"
            },
            "must_have": {"type": "array", "items": {"type": "string"}},
            "nice_to_have": {"type": "array", "items": {"type": "string"}},
            "time_horizon": {"type": "string", "default": "12m"}
        },
        "required": ["intent"]
    }
    
    # Use LLM tool to extract structured data
    try:
        parsed_data = await llm_tool.nlu_extract(text, extraction_schema)
        
        # Add confidence score if not present
        if "confidence" not in parsed_data:
            parsed_data["confidence"] = 0.8  # Default confidence
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"LLM extraction failed: {str(e)}")
        # Fallback to basic parsing
        return _fallback_parsing(text, locale)


def _fallback_parsing(text: str, locale: str) -> Dict[str, Any]:
    """
    Fallback parsing when LLM extraction fails.
    
    Args:
        text: Raw user query
        locale: User locale
        
    Returns:
        Basic parsed data
    """
    text_lower = text.lower()
    
    # Basic keyword extraction
    goals = []
    if any(word in text_lower for word in ["miles", "travel", "airline"]):
        goals.extend(["miles", "travel"])
    if any(word in text_lower for word in ["cashback", "cash back", "money"]):
        goals.append("cashback")
    if any(word in text_lower for word in ["rewards", "points"]):
        goals.append("rewards")
    
    # Basic constraints
    constraints = {}
    if "no fee" in text_lower or "no annual fee" in text_lower:
        constraints["annual_fee_max"] = 0
    
    # Parse jurisdiction from locale
    jurisdiction = _parse_jurisdiction_from_locale(locale)
    
    return {
        "intent": "recommend_card",
        "goals": goals if goals else ["rewards"],
        "constraints": constraints,
        "jurisdiction": jurisdiction,
        "risk_tolerance": "standard",
        "time_horizon": "12m",
        "confidence": 0.5  # Lower confidence for fallback
    }


def _parse_jurisdiction_from_locale(locale: str) -> str:
    """
    Parse jurisdiction from locale string.
    
    Args:
        locale: Locale string (e.g., "en-SG", "fr-FR", "de-DE")
        
    Returns:
        Jurisdiction code (e.g., "SG", "FR", "DE")
    """
    if not locale:
        return "SG"  # Default
    
    # Handle standard format: "en-SG", "fr-FR", etc.
    if "-" in locale:
        return locale.split("-")[-1]
    
    # Handle 2-letter codes: "SG", "US", etc.
    if len(locale) == 2:
        return locale
    
    # Handle longer codes: "enUS", "enGB", etc.
    if len(locale) > 2:
        if locale.startswith("en"):
            return locale[2:]
        else:
            return locale
    
    # Default fallback
    return "SG"


async def _validate_request(policy_tool: PolicyTool, parsed_data: Dict[str, Any], consent: Any, locale: str) -> RequestParsed:
    """
    Validate and create RequestParsed object.
    
    Args:
        policy_tool: Policy tool for validation
        parsed_data: Parsed data from LLM
        consent: User consent object
        locale: User locale for jurisdiction override
        
    Returns:
        Validated RequestParsed object
    """
    # Apply consent-based filtering
    if not consent.personalization:
        # Remove personalization-heavy fields
        parsed_data.pop("spend_focus", None)
        parsed_data.pop("priority", None)
    
    # Override jurisdiction with locale if it doesn't match
    expected_jurisdiction = _parse_jurisdiction_from_locale(locale)
    if parsed_data.get("jurisdiction") != expected_jurisdiction:
        logger.info(f"Overriding jurisdiction from {parsed_data.get('jurisdiction')} to {expected_jurisdiction} based on locale {locale}")
        parsed_data["jurisdiction"] = expected_jurisdiction
    
    # Ensure required fields have defaults
    defaults = {
        "constraints": {},
        "goals": ["rewards"],
        "priority": [],
        "spend_focus": {},
        "jurisdiction": expected_jurisdiction,
        "risk_tolerance": "standard",
        "must_have": [],
        "nice_to_have": [],
        "time_horizon": "12m"
    }
    
    for key, default_value in defaults.items():
        if key not in parsed_data:
            parsed_data[key] = default_value
    
    # Create and validate RequestParsed object
    try:
        request = RequestParsed(**parsed_data)
        return request
    except Exception as e:
        logger.error(f"Request validation failed: {str(e)}")
        # Return minimal valid request
        return RequestParsed(
            intent="recommend_card",
            goals=["rewards"],
            jurisdiction=expected_jurisdiction
        )

