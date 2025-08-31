"""
Core state models for the Credit Card Recommendation Agent.
Refactored to use LangGraph properly.
"""

from typing import Dict, List, Optional, Any, Union, Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class Consent(BaseModel):
    """User consent object for data processing."""
    personalization: bool = Field(default=False, description="Allow personalization")
    data_sharing: bool = Field(default=False, description="Allow data sharing")
    credit_pull: str = Field(default="none", description="Credit pull consent level")


class RequestParsed(BaseModel):
    """Parsed request from Extractor Agent."""
    intent: str = Field(description="Recommendation intent")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="User constraints")
    goals: List[str] = Field(default_factory=list, description="User goals")
    priority: List[str] = Field(default_factory=list, description="Priority order")
    spend_focus: Dict[str, float] = Field(default_factory=dict, description="Spending patterns")
    jurisdiction: str = Field(description="Geographic jurisdiction")
    risk_tolerance: str = Field(default="standard", description="Risk tolerance level")
    must_have: List[str] = Field(default_factory=list, description="Must-have features")
    nice_to_have: List[str] = Field(default_factory=list, description="Nice-to-have features")
    time_horizon: str = Field(default="12m", description="Time horizon for recommendations")


# Note: CardRecommendation and ManagerResult are defined in src/nodes/card_managers.py
# We'll import them there to avoid duplication


class FinalRecommendations(BaseModel):
    """Final aggregated recommendations from Summary Agent."""
    recommendations: List[Any] = Field(description="Top recommendations")  # Will be FinalRecommendation from summary
    alternatives: List[str] = Field(default_factory=list, description="Alternative card IDs")
    notes: Dict[str, Any] = Field(default_factory=dict, description="Additional notes")


class TelemetryEvent(BaseModel):
    """Telemetry event for observability."""
    name: str = Field(default="unknown", description="Event name")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")


class Message(BaseModel):
    """Message envelope for inter-node communication."""
    type: str = Field(description="Message type: NODE_REQUEST, NODE_RESPONSE, ERROR")
    from_node: str = Field(description="Source node identifier")
    to_node: str = Field(description="Target node identifier")
    idempotency_key: UUID = Field(description="Idempotency key")
    payload: Dict[str, Any] = Field(description="Message payload")
    status: Optional[str] = Field(default=None, description="Status: OK, NO_MATCH, RETRY, ERROR")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")


# LangGraph State Definition using Pydantic BaseModel
class GraphState(BaseModel):
    """Global graph state for LangGraph orchestration."""
    # Session information
    session_id: str = Field(description="Unique session identifier")
    user_query: str = Field(description="User's credit card request")
    locale: str = Field(default="en-SG", description="User's locale")
    
    # User consent
    consent: Consent = Field(description="User consent object")
    
    # Processing state
    request: Optional[RequestParsed] = Field(default=None, description="Parsed request")
    policy_pack: Dict[str, Any] = Field(default_factory=dict, description="Policy configuration")
    catalog_meta: Dict[str, Any] = Field(default_factory=dict, description="Catalog metadata")
    
    # Agent orchestration
    fanout_plan: Optional[List[str]] = Field(default=None, description="Planned manager categories")
    manager_results: Dict[str, Any] = Field(default_factory=dict, description="Results from managers")  # Will be ManagerResult from card_managers
    final_recommendations: Optional[Any] = Field(default=None, description="Final recommendations")  # Will be SummaryResult from summary
    
    # Observability
    telemetry: Dict[str, Any] = Field(default_factory=dict, description="Telemetry data")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error tracking")
    
    # Node tracking
    current_node: Optional[str] = Field(default=None, description="Currently executing node")
    completed_nodes: List[str] = Field(default_factory=list, description="Completed nodes")
    next_nodes: List[str] = Field(default_factory=list, description="Next nodes to execute")

