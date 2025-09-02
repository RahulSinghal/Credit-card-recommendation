#!/usr/bin/env python3
"""
Support Agents
Online Search and Policy validation agents for the credit card recommendation system.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.models.state import GraphState, RequestParsed
from src.tools.base import LLMTool, PolicyTool, CatalogTool


@dataclass
class SearchResult:
    """Result from online search."""
    source: str
    title: str
    content: str
    relevance_score: float
    url: Optional[str] = None
    timestamp: Optional[float] = None


@dataclass
class PolicyValidationResult:
    """Result from policy validation."""
    is_valid: bool
    warnings: List[str]
    required_consent: List[str]
    compliance_issues: List[str]
    recommendations: List[str]


class OnlineSearchAgent:
    """Agent for searching online information about credit cards."""
    
    def __init__(self, llm_tool: LLMTool):
        self.llm_tool = llm_tool
        self.agent_type = "online_search"
    
    async def search_credit_card_info(self, query: str, card_name: str = None) -> List[SearchResult]:
        """Search for credit card information online."""
        try:
            # In a real implementation, this would call actual search APIs
            # For now, we'll simulate search results
            
            search_results = []
            
            if "travel" in query.lower() or "miles" in query.lower():
                search_results.append(SearchResult(
                    source="Credit Card Review Site",
                    title="Best Travel Credit Cards 2024",
                    content="Top travel credit cards with airline miles and hotel benefits. Compare annual fees and signup bonuses.",
                    relevance_score=0.9,
                    url="https://example.com/travel-cards-2024",
                    timestamp=time.time()
                ))
                
                search_results.append(SearchResult(
                    source="Bank Website",
                    title="Travel Rewards Program",
                    content="Earn miles on every purchase. No foreign transaction fees. Travel insurance included.",
                    relevance_score=0.8,
                    url="https://example.com/travel-rewards",
                    timestamp=time.time()
                ))
            
            if "cashback" in query.lower() or "rewards" in query.lower():
                search_results.append(SearchResult(
                    source="Financial Blog",
                    title="Cashback vs Points: Which is Better?",
                    content="Detailed comparison of cashback and points credit cards. Learn which type fits your spending habits.",
                    relevance_score=0.85,
                    url="https://example.com/cashback-vs-points",
                    timestamp=time.time()
                ))
            
            if "business" in query.lower() or "corporate" in query.lower():
                search_results.append(SearchResult(
                    source="Business Finance Site",
                    title="Business Credit Card Guide",
                    content="Essential guide to business credit cards. Employee cards, expense tracking, and corporate benefits.",
                    relevance_score=0.9,
                    url="https://example.com/business-cards",
                    timestamp=time.time()
                ))
            
            if "student" in query.lower() or "building credit" in query.lower():
                search_results.append(SearchResult(
                    source="Student Finance Blog",
                    title="First Credit Card for Students",
                    content="How to build credit as a student. Best first credit cards with no annual fees.",
                    relevance_score=0.9,
                    url="https://example.com/student-cards",
                    timestamp=time.time()
                ))
            
            # Add general information
            search_results.append(SearchResult(
                source="Credit Card Comparison",
                title="Credit Card Basics",
                content="Understanding annual fees, interest rates, and rewards programs. Tips for choosing the right card.",
                relevance_score=0.7,
                url="https://example.com/credit-card-basics",
                timestamp=time.time()
            ))
            
            # Sort by relevance score
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return search_results[:5]  # Return top 5 results
            
        except Exception as e:
            # Return empty results on error
            return []
    
    async def search_card_specific_info(self, card_name: str) -> List[SearchResult]:
        """Search for information about a specific credit card."""
        try:
            search_results = []
            
            # Simulate card-specific search results
            if "krisflyer" in card_name.lower():
                search_results.append(SearchResult(
                    source="Singapore Airlines",
                    title="KrisFlyer Credit Card Benefits",
                    content="Earn KrisFlyer miles on every purchase. Exclusive travel benefits and airport lounge access.",
                    relevance_score=0.95,
                    url="https://example.com/krisflyer-card",
                    timestamp=time.time()
                ))
            
            elif "live fresh" in card_name.lower():
                search_results.append(SearchResult(
                    source="DBS Bank",
                    title="Live Fresh Card Features",
                    content="5% cashback on online spending. No annual fee. Perfect for digital lifestyle.",
                    relevance_score=0.95,
                    url="https://example.com/live-fresh-card",
                    timestamp=time.time()
                ))
            
            elif "business" in card_name.lower():
                search_results.append(SearchResult(
                    source="UOB Bank",
                    title="Business Card Solutions",
                    content="Corporate expense management. Employee card programs. Business rewards and benefits.",
                    relevance_score=0.9,
                    url="https://example.com/business-card",
                    timestamp=time.time()
                ))
            
            # Add general card information
            search_results.append(SearchResult(
                source="Card Review Site",
                title=f"{card_name} Review",
                content=f"Comprehensive review of {card_name}. Pros, cons, and user experiences.",
                relevance_score=0.8,
                url=f"https://example.com/{card_name.lower().replace(' ', '-')}-review",
                timestamp=time.time()
            ))
            
            return search_results
            
        except Exception as e:
            return []
    
    async def execute(self, state: GraphState) -> GraphState:
        """Execute the online search agent."""
        start_time = time.time()
        
        try:
            # Update state
            state.current_node = self.agent_type
            state.completed_nodes.append(self.agent_type)
            
            # Get the user query and any card names from manager results
            user_query = state.user_query
            card_names = []
            
            # Extract card names from manager results
            if state.manager_results:
                for manager_type, manager_result in state.manager_results.items():
                    if hasattr(manager_result, 'recommendations'):
                        for rec in manager_result.recommendations:
                            if hasattr(rec, 'card_name'):
                                card_names.append(rec.card_name)
            
            # Perform searches
            general_search_results = await self.search_credit_card_info(user_query)
            card_specific_results = []
            
            for card_name in card_names[:3]:  # Limit to top 3 cards
                card_results = await self.search_card_specific_info(card_name)
                card_specific_results.extend(card_results)
            
            # Combine and deduplicate results
            all_results = general_search_results + card_specific_results
            unique_results = {}
            
            for result in all_results:
                key = f"{result.source}:{result.title}"
                if key not in unique_results or result.relevance_score > unique_results[key].relevance_score:
                    unique_results[key] = result
            
            # Sort by relevance and take top results
            final_results = sorted(unique_results.values(), key=lambda x: x.relevance_score, reverse=True)[:8]
            
            # Store results in state
            if not hasattr(state, 'online_search_results'):
                state.online_search_results = {}
            
            state.online_search_results = {
                "general_search": general_search_results,
                "card_specific_search": card_specific_results,
                "combined_results": final_results,
                "search_time": time.time() - start_time,
                "total_results": len(final_results)
            }
            
            state.next_nodes = ["policy_validation"]
            return state
            
        except Exception as e:
            # Handle errors gracefully
            error_info = {
                "node": self.agent_type,
                "error": str(e),
                "timestamp": time.time()
            }
            state.errors.append(error_info)
            state.next_nodes = ["policy_validation"]
            return state


class PolicyValidationAgent:
    """Agent for validating requests against policies and regulations."""
    
    def __init__(self, policy_tool: PolicyTool):
        self.policy_tool = policy_tool
        self.agent_type = "policy_validation"
    
    async def validate_request_compliance(self, request: RequestParsed, consent: Any) -> PolicyValidationResult:
        """Validate request against compliance policies."""
        try:
            # Get policy pack for the jurisdiction
            policy_pack = await self.policy_tool.get_policy_pack(
                request.jurisdiction, 
                "en-SG"  # Default locale
            )
            
            # Validate the request
            validation_result = await self.policy_tool.validate_request(
                request.dict(), 
                policy_pack
            )
            
            # Create policy validation result
            warnings = []
            compliance_issues = []
            recommendations = []
            
            if not validation_result.get("valid", True):
                warnings.append("Request validation failed")
            
            # Check consent requirements
            required_consent = validation_result.get("required_consent", [])
            if "personalization" in required_consent and not consent.personalization:
                warnings.append("Personalization consent required for better recommendations")
                recommendations.append("Enable personalization for tailored results")
            
            if "data_sharing" in required_consent and not consent.data_sharing:
                warnings.append("Data sharing consent required for comprehensive analysis")
                recommendations.append("Enable data sharing for detailed insights")
            
            # Check jurisdiction-specific compliance
            if request.jurisdiction == "SG":
                if not policy_pack.get("compliance", {}).get("gdpr", False):
                    compliance_issues.append("GDPR compliance not applicable for Singapore")
                recommendations.append("Singapore regulations apply")
            
            elif request.jurisdiction == "US":
                if not policy_pack.get("compliance", {}).get("ccpa", False):
                    compliance_issues.append("CCPA compliance not applicable for US")
                recommendations.append("US regulations apply")
            
            # Add general recommendations
            if request.risk_tolerance == "aggressive":
                recommendations.append("Consider conservative options for better approval chances")
            
            if request.time_horizon == "12m":
                recommendations.append("Focus on cards with good signup bonuses")
            
            return PolicyValidationResult(
                is_valid=validation_result.get("valid", True),
                warnings=warnings,
                required_consent=required_consent,
                compliance_issues=compliance_issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            # Return basic validation result on error
            return PolicyValidationResult(
                is_valid=True,  # Assume valid on error
                warnings=[f"Policy validation error: {str(e)}"],
                required_consent=["personalization", "data_sharing"],
                compliance_issues=[],
                recommendations=["Contact support for policy validation"]
            )
    
    async def execute(self, state: GraphState) -> GraphState:
        """Execute the policy validation agent."""
        start_time = time.time()
        
        try:
            # Update state
            state.current_node = self.agent_type
            state.completed_nodes.append(self.agent_type)
            
            # Validate request compliance
            if state.request and state.consent:
                validation_result = await self.validate_request_compliance(
                    state.request, 
                    state.consent
                )
                
                # Store validation result in state
                if not hasattr(state, 'policy_validation'):
                    state.policy_validation = {}
                
                state.policy_validation = {
                    "validation_result": validation_result,
                    "validation_time": time.time() - start_time,
                    "is_compliant": validation_result.is_valid
                }
                
                # Add warnings to errors if any
                if validation_result.warnings:
                    for warning in validation_result.warnings:
                        state.errors.append({
                            "node": self.agent_type,
                            "error": warning,
                            "timestamp": time.time(),
                            "type": "warning"
                        })
            else:
                # No request or consent to validate
                state.policy_validation = {
                    "validation_result": None,
                    "validation_time": time.time() - start_time,
                    "is_compliant": True
                }
            
            state.next_nodes = ["summary"]  # Next step is summary
            return state
            
        except Exception as e:
            # Handle errors gracefully
            error_info = {
                "node": self.agent_type,
                "error": str(e),
                "timestamp": time.time()
            }
            state.errors.append(error_info)
            state.next_nodes = ["summary"]
            return state


# Factory functions to create support agent nodes
def create_online_search_node() -> callable:
    """Create a LangGraph-compatible node for the online search agent."""
    
    async def online_search_node(state: GraphState) -> GraphState:
        """LangGraph node function for online search agent execution."""
        # Create mock tools for now
        from src.tools.mock_tools import MockLLMTool
        
        mock_llm = MockLLMTool()
        
        online_search_agent = OnlineSearchAgent(mock_llm)
        
        # Execute the agent
        return await online_search_agent.execute(state)
    
    return online_search_node


def create_policy_validation_node() -> callable:
    """Create a LangGraph-compatible node for the policy validation agent."""
    
    async def policy_validation_node(state: GraphState) -> GraphState:
        """LangGraph node function for policy validation agent execution."""
        # Create mock tools for now
        from src.tools.mock_tools import MockPolicyTool
        
        mock_policy = MockPolicyTool()
        
        policy_validation_agent = PolicyValidationAgent(mock_policy)
        
        # Execute the agent
        return await policy_validation_agent.execute(state)
    
    return policy_validation_node

