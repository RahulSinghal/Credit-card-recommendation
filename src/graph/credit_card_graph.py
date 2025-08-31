#!/usr/bin/env python3
"""
Credit Card Recommendation Graph
Main LangGraph orchestration for the multi-agent credit card recommendation system.
"""

from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.models.state import GraphState, RequestParsed
from src.nodes.extractor import create_extractor_node
from src.nodes.card_managers import (
    create_travel_manager_node,
    create_cashback_manager_node,
    create_business_manager_node,
    create_student_manager_node,
    create_general_manager_node
)
from src.nodes.summary import create_summary_node
from src.nodes.support_agents import create_online_search_node, create_policy_validation_node
from src.nodes.error_handler import create_error_handler_node


def create_credit_card_graph(llm_tool, policy_tool) -> StateGraph:
    """Create the complete credit card recommendation graph."""
    
    # Create the graph
    workflow = StateGraph(GraphState)
    
    # Add all nodes
    workflow.add_node("extractor", create_extractor_node(llm_tool, policy_tool))
    workflow.add_node("router", _create_router_node())
    workflow.add_node("travel_manager", create_travel_manager_node())
    workflow.add_node("cashback_manager", create_cashback_manager_node())
    workflow.add_node("business_manager", create_business_manager_node())
    workflow.add_node("student_manager", create_student_manager_node())
    workflow.add_node("general_manager", create_general_manager_node())
    workflow.add_node("online_search", create_online_search_node())
    workflow.add_node("policy_validation", create_policy_validation_node())
    workflow.add_node("error_handler", create_error_handler_node())
    workflow.add_node("summary", create_summary_node())
    
    # Set entry point
    workflow.set_entry_point("extractor")
    
    # Add conditional edges from extractor
    workflow.add_conditional_edges(
        "extractor",
        _should_continue_to_router,
        {
            "router": "router",
            "error_handler": "error_handler",
            END: END
        }
    )
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        _should_continue_to_managers,
        {
            "travel_manager": "travel_manager",
            "cashback_manager": "cashback_manager",
            "business_manager": "business_manager",
            "student_manager": "student_manager",
            "general_manager": "general_manager",
            "error_handler": "error_handler",
            END: END
        }
    )
    
    # Add edges from card managers to online search
    workflow.add_edge("travel_manager", "online_search")
    workflow.add_edge("cashback_manager", "online_search")
    workflow.add_edge("business_manager", "online_search")
    workflow.add_edge("student_manager", "online_search")
    workflow.add_edge("general_manager", "online_search")
    
    # Add edge from online search to policy validation
    workflow.add_edge("online_search", "policy_validation")
    
    # Add edge from policy validation to summary
    workflow.add_edge("policy_validation", "summary")
    
    # Add edge from error handler to summary
    workflow.add_edge("error_handler", "summary")
    
    # Add edge from summary to END
    workflow.add_edge("summary", END)
    
    # Compile the graph
    return workflow.compile()


def _create_router_node():
    """Create the router node for determining which card managers to invoke."""
    import time
    
    async def router_node(state: GraphState) -> GraphState:
        """Route to appropriate card managers based on user goals."""
        try:
            # Update state
            state.current_node = "router"
            state.completed_nodes.append("router")
            
            # Get the parsed request
            request = state.request
            if not request:
                state.errors.append({
                    "node": "router",
                    "error": "No parsed request available",
                    "timestamp": time.time()
                })
                state.next_nodes = ["error_handler"]
                return state
            
            # Determine which managers to invoke
            manager_categories = _determine_manager_categories(request)
            
            # Create fanout plan
            state.fanout_plan = manager_categories
            
            # Set next nodes based on the plan
            if manager_categories:
                state.next_nodes = manager_categories
            else:
                # Fallback to general manager
                state.next_nodes = ["general_manager"]
            
            return state
            
        except Exception as e:
            # Handle errors gracefully
            state.errors.append({
                "node": "router",
                "error": f"Router error: {str(e)}",
                "timestamp": time.time()
            })
            state.next_nodes = ["error_handler"]
            return state
    
    return router_node


def _determine_manager_categories(request: RequestParsed) -> List[str]:
    """Determine which card manager categories to invoke based on user goals."""
    manager_categories = []
    
    goals = request.goals or []
    
    # Map goals to managers
    if any(goal in goals for goal in ["miles", "travel", "airline", "hotel"]):
        manager_categories.append("travel_manager")
    
    if any(goal in goals for goal in ["cashback", "cash", "rewards", "money"]):
        manager_categories.append("cashback_manager")
    
    if any(goal in goals for goal in ["business", "corporate", "expense", "employee"]):
        manager_categories.append("business_manager")
    
    if any(goal in goals for goal in ["student", "building_credit", "first", "college"]):
        manager_categories.append("student_manager")
    
    # If no specific managers identified, use general manager
    if not manager_categories:
        manager_categories.append("general_manager")
    
    return manager_categories


def _should_continue_to_router(state: GraphState) -> str:
    """Determine if we should continue to router or handle errors."""
    if state.errors:
        return "error_handler"
    
    if state.request:
        return "router"
    
    return END


def _should_continue_to_managers(state: GraphState) -> str:
    """Determine which manager to route to."""
    if state.errors:
        return "error_handler"
    
    if state.fanout_plan:
        # Return the first manager in the plan
        return state.fanout_plan[0]
    
    return "general_manager"


def create_initial_state(user_query: str) -> GraphState:
    """Create initial state for the graph."""
    import time
    from src.models.state import Consent
    
    return GraphState(
        session_id=f"session_{int(time.time())}",
        user_query=user_query,
        locale="en-SG",
        consent=Consent(
            personalization=True,
            data_sharing=False,
            credit_pull="none"
        ),
        request=None,
        policy_pack={},
        catalog_meta={},
        fanout_plan=None,
        manager_results={},
        final_recommendations=None,
        telemetry={"events": []},
        errors=[],
        current_node=None,
        completed_nodes=[],
        next_nodes=[]
    )
