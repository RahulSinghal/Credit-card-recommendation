#!/usr/bin/env python3
"""
Error Handler Node
Handles errors gracefully and provides fallback responses.
"""

import time
from typing import Dict, List, Any
from dataclasses import dataclass
from src.models.state import GraphState, RequestParsed
from src.tools.base import LLMTool, PolicyTool


@dataclass
class ErrorHandlingResult:
    """Result from error handling."""
    errors_handled: int
    user_friendly_message: str
    recovery_actions: List[str]
    can_continue: bool
    fallback_recommendations: List[Dict[str, Any]]


class ErrorHandlerNode:
    """Node for handling errors gracefully in the graph."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool):
        self.llm_tool = llm_tool
        self.policy_tool = policy_tool
        self.node_type = "error_handler"
    
    def generate_user_friendly_message(self, errors: List[Dict[str, Any]]) -> str:
        """Generate a user-friendly error message."""
        if not errors:
            return "No errors occurred during processing."
        
        return "We encountered some issues but your recommendations are still available below."
    
    def generate_recovery_actions(self, errors: List[Dict[str, Any]]) -> List[str]:
        """Generate recovery action suggestions."""
        return ["Review the recommendations below", "Contact support if issues persist"]
    
    def generate_fallback_recommendations(self, request: RequestParsed) -> List[Dict[str, Any]]:
        """Generate fallback recommendations when errors occur."""
        return [{
            "card_id": "fallback_001",
            "card_name": "Standard Rewards Card",
            "card_type": "rewards",
            "issuer": "Major Bank",
            "annual_fee": 49.0,
            "rewards_rate": "1% cashback on all purchases",
            "signup_bonus": "$100 cashback",
            "credit_score_required": "good",
            "pros": ["Simple rewards", "Moderate annual fee"],
            "cons": ["Basic benefits", "No category bonuses"],
            "match_score": 0.6,
            "reasoning": "Fallback recommendation"
        }]
    
    def can_continue_execution(self, errors: List[Dict[str, Any]]) -> bool:
        """Determine if the graph can continue execution."""
        return True  # Always continue for now
    
    async def execute(self, state: GraphState) -> GraphState:
        """Execute the error handler node."""
        start_time = time.time()
        
        try:
            # Update state
            state.current_node = self.node_type
            state.completed_nodes.append(self.node_type)
            
            # Get errors from state
            errors = state.errors or []
            
            # Generate error handling result
            user_friendly_message = self.generate_user_friendly_message(errors)
            recovery_actions = self.generate_recovery_actions(errors)
            can_continue = self.can_continue_execution(errors)
            
            # Generate fallback recommendations if needed
            fallback_recommendations = []
            if can_continue and state.request:
                fallback_recommendations = self.generate_fallback_recommendations(state.request)
            
            # Create error handling result
            error_handling_result = ErrorHandlingResult(
                errors_handled=len(errors),
                user_friendly_message=user_friendly_message,
                recovery_actions=recovery_actions,
                can_continue=can_continue,
                fallback_recommendations=fallback_recommendations
            )
            
            # Store error handling result in state
            if not hasattr(state, 'error_handling'):
                state.error_handling = {}
            
            state.error_handling = {
                "result": error_handling_result,
                "handling_time": time.time() - start_time,
                "total_errors": len(errors)
            }
            
            # Set next nodes
            state.next_nodes = ["summary"]
            
            return state
            
        except Exception as e:
            # Handle errors in the error handler itself
            error_info = {
                "node": self.node_type,
                "error": f"Error handler failed: {str(e)}",
                "timestamp": time.time(),
                "type": "critical"
            }
            state.errors.append(error_info)
            state.next_nodes = []
            return state


# Factory function to create error handler node
def create_error_handler_node() -> callable:
    """Create a LangGraph-compatible node for the error handler."""
    
    async def error_handler_node(state: GraphState) -> GraphState:
        """LangGraph node function for error handler execution."""
        # Create mock tools for now
        from src.tools.mock_tools import MockLLMTool, MockPolicyTool
        
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        
        error_handler = ErrorHandlerNode(mock_llm, mock_policy)
        
        # Execute the error handler
        return await error_handler.execute(state)
    
    return error_handler_node

