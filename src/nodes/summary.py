#!/usr/bin/env python3
"""
Summary Agent
Aggregates results from all card managers and provides final recommendations.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.models.state import GraphState, RequestParsed
from src.tools.base import LLMTool, PolicyTool
from src.nodes.card_managers import CardRecommendation, ManagerResult


@dataclass
class FinalRecommendation:
    """Final aggregated recommendation for the user."""
    card_id: str
    card_name: str
    card_type: str
    issuer: str
    annual_fee: float
    rewards_rate: str
    signup_bonus: str
    credit_score_required: str
    pros: List[str]
    cons: List[str]
    overall_score: float  # 0.0 to 1.0
    manager_scores: Dict[str, float]  # Scores from each manager
    reasoning: str
    best_for: List[str]  # What this card is best for


@dataclass
class SummaryResult:
    """Result from the summary agent."""
    total_cards_analyzed: int
    final_recommendations: List[FinalRecommendation]
    top_recommendation: Optional[FinalRecommendation]
    summary_text: str
    execution_time: float
    confidence_score: float


class SummaryAgent:
    """Aggregates and summarizes recommendations from all card managers."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool):
        self.llm_tool = llm_tool
        self.policy_tool = policy_tool
        self.agent_type = "summary"
    
    async def aggregate_manager_results(self, manager_results: Dict[str, ManagerResult]) -> List[CardRecommendation]:
        """Aggregate all recommendations from different managers."""
        all_recommendations = []
        
        for manager_type, manager_result in manager_results.items():
            if manager_result.recommendations:
                all_recommendations.extend(manager_result.recommendations)
        
        return all_recommendations
    
    def calculate_overall_score(self, card: CardRecommendation, manager_results: Dict[str, ManagerResult]) -> float:
        """Calculate overall score considering all manager inputs."""
        # Start with the card's base match score
        overall_score = card.match_score
        
        # Boost score based on how many managers recommended this card
        manager_count = 0
        manager_scores = {}
        
        for manager_type, manager_result in manager_results.items():
            # Check if this card was recommended by this manager
            for rec in manager_result.recommendations:
                if rec.card_id == card.card_id:
                    manager_count += 1
                    manager_scores[manager_type] = rec.match_score
                    # Boost score for multi-manager recommendations
                    overall_score += 0.1
        
        # Cap at 1.0
        return min(overall_score, 1.0)
    
    def identify_best_features(self, card: CardRecommendation, request: RequestParsed) -> List[str]:
        """Identify what this card is best for."""
        best_features = []
        
        # Analyze based on card type and features
        if card.card_type == "travel":
            if "miles" in card.rewards_rate.lower():
                best_features.append("Airline miles earning")
            if "no foreign transaction fee" in str(card).lower():
                best_features.append("International travel")
            if "travel insurance" in str(card).lower():
                best_features.append("Travel protection")
        
        elif card.card_type == "cashback":
            if "%" in card.rewards_rate:
                best_features.append("Cashback rewards")
            if "online" in card.rewards_rate.lower():
                best_features.append("Online shopping")
            if "dining" in card.rewards_rate.lower():
                best_features.append("Dining rewards")
        
        elif card.card_type == "business":
            best_features.append("Business expenses")
            if "employee" in str(card).lower():
                best_features.append("Employee cards")
        
        elif card.card_type == "student":
            best_features.append("Credit building")
            if card.annual_fee == 0:
                best_features.append("No annual fee")
        
        # Add general features
        if card.annual_fee == 0:
            best_features.append("Cost-effective")
        elif card.annual_fee <= 50:
            best_features.append("Low cost")
        
        if "signup bonus" in str(card).lower():
            best_features.append("Signup bonus")
        
        return best_features
    
    def generate_reasoning(self, card: CardRecommendation, overall_score: float, best_features: List[str]) -> str:
        """Generate reasoning for the final recommendation."""
        reasoning_parts = []
        
        if overall_score > 0.9:
            reasoning_parts.append("Excellent overall match")
        elif overall_score > 0.7:
            reasoning_parts.append("Strong recommendation")
        elif overall_score > 0.5:
            reasoning_parts.append("Good option to consider")
        else:
            reasoning_parts.append("Basic match")
        
        if best_features:
            reasoning_parts.append(f"Best for: {', '.join(best_features)}")
        
        if card.annual_fee == 0:
            reasoning_parts.append("No annual fee makes it cost-effective")
        elif card.annual_fee <= 50:
            reasoning_parts.append("Low annual fee for good value")
        
        return ". ".join(reasoning_parts)
    
    async def create_final_recommendations(
        self, 
        all_cards: List[CardRecommendation], 
        manager_results: Dict[str, ManagerResult],
        request: RequestParsed
    ) -> List[FinalRecommendation]:
        """Create final recommendations with overall scoring."""
        final_recommendations = []
        
        for card in all_cards:
            # Calculate overall score
            overall_score = self.calculate_overall_score(card, manager_results)
            
            # Identify best features
            best_features = self.identify_best_features(card, request)
            
            # Generate reasoning
            reasoning = self.generate_reasoning(card, overall_score, best_features)
            
            # Get manager scores
            manager_scores = {}
            for manager_type, manager_result in manager_results.items():
                for rec in manager_result.recommendations:
                    if rec.card_id == card.card_id:
                        manager_scores[manager_type] = rec.match_score
            
            # Create final recommendation
            final_rec = FinalRecommendation(
                card_id=card.card_id,
                card_name=card.card_name,
                card_type=card.card_type,
                issuer=card.issuer,
                annual_fee=card.annual_fee,
                rewards_rate=card.rewards_rate,
                signup_bonus=card.signup_bonus,
                credit_score_required=card.credit_score_required,
                pros=card.pros,
                cons=card.cons,
                overall_score=overall_score,
                manager_scores=manager_scores,
                reasoning=reasoning,
                best_for=best_features
            )
            
            final_recommendations.append(final_rec)
        
        # Sort by overall score (highest first)
        final_recommendations.sort(key=lambda x: x.overall_score, reverse=True)
        
        return final_recommendations
    
    async def generate_summary_text(
        self, 
        final_recommendations: List[FinalRecommendation], 
        request: RequestParsed
    ) -> str:
        """Generate human-readable summary text."""
        if not final_recommendations:
            return "No suitable credit cards found based on your requirements."
        
        top_card = final_recommendations[0]
        
        summary_parts = [
            f"Based on your goals of {', '.join(request.goals)}, I've analyzed {len(final_recommendations)} credit cards.",
            f"Here's my top recommendation:",
            f"🏆 {top_card.card_name} by {top_card.issuer}",
            f"   • {top_card.rewards_rate}",
            f"   • Annual fee: S${top_card.annual_fee}",
            f"   • Signup bonus: {top_card.signup_bonus}",
            f"   • Best for: {', '.join(top_card.best_for)}",
            f"   • Overall score: {top_card.overall_score:.2f}/1.0"
        ]
        
        if len(final_recommendations) > 1:
            summary_parts.append(f"\nI also found {len(final_recommendations)-1} other good options to consider.")
        
        return "\n".join(summary_parts)
    
    async def execute(self, state: GraphState) -> GraphState:
        """Execute the summary agent."""
        import time
        start_time = time.time()
        
        try:
            # Update state
            state.current_node = self.agent_type
            state.completed_nodes.append(self.agent_type)
            
            # Get manager results
            manager_results = state.manager_results
            
            if not manager_results:
                # No manager results to summarize
                summary_result = SummaryResult(
                    total_cards_analyzed=0,
                    final_recommendations=[],
                    top_recommendation=None,
                    summary_text="No card manager results available for summarization.",
                    execution_time=time.time() - start_time,
                    confidence_score=0.0
                )
                
                state.final_recommendations = summary_result
                state.next_nodes = []
                return state
            
            # Aggregate all recommendations
            all_cards = await self.aggregate_manager_results(manager_results)
            
            if not all_cards:
                summary_result = SummaryResult(
                    total_cards_analyzed=0,
                    final_recommendations=[],
                    top_recommendation=None,
                    summary_text="No credit card recommendations found from managers.",
                    execution_time=time.time() - start_time,
                    confidence_score=0.0
                )
                
                state.final_recommendations = summary_result
                state.next_nodes = []
                return state
            
            # Create final recommendations
            final_recommendations = await self.create_final_recommendations(
                all_cards, manager_results, state.request
            )
            
            # Generate summary text
            summary_text = await self.generate_summary_text(final_recommendations, state.request)
            
            # Calculate confidence score
            confidence_score = 0.0
            if final_recommendations:
                # Average of top 3 recommendations
                top_scores = [rec.overall_score for rec in final_recommendations[:3]]
                confidence_score = sum(top_scores) / len(top_scores)
            
            # Create summary result
            summary_result = SummaryResult(
                total_cards_analyzed=len(all_cards),
                final_recommendations=final_recommendations,
                top_recommendation=final_recommendations[0] if final_recommendations else None,
                summary_text=summary_text,
                execution_time=time.time() - start_time,
                confidence_score=confidence_score
            )
            
            # Update state
            state.final_recommendations = summary_result
            state.next_nodes = []  # End of workflow
            
            return state
            
        except Exception as e:
            # Handle errors gracefully
            error_info = {
                "node": self.agent_type,
                "error": str(e),
                "timestamp": time.time()
            }
            state.errors.append(error_info)
            state.next_nodes = []
            return state


# Factory function to create summary node
def create_summary_node() -> callable:
    """Create a LangGraph-compatible node for the summary agent."""
    
    async def summary_node(state: GraphState) -> GraphState:
        """LangGraph node function for summary agent execution."""
        # Create mock tools for now
        from src.tools.mock_tools import MockLLMTool, MockPolicyTool
        
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        
        summary_agent = SummaryAgent(mock_llm, mock_policy)
        
        # Execute the agent
        return await summary_agent.execute(state)
    
    return summary_node
