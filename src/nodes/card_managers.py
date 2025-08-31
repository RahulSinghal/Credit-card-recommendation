#!/usr/bin/env python3
"""
Card Manager Agents
Specialized agents for different types of credit card recommendations.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.models.state import GraphState, RequestParsed
from src.tools.base import LLMTool, PolicyTool, CatalogTool


@dataclass
class CardRecommendation:
    """Represents a credit card recommendation."""
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
    match_score: float  # 0.0 to 1.0
    reasoning: str


@dataclass
class ManagerResult:
    """Result from a card manager agent."""
    manager_type: str
    recommendations: List[CardRecommendation]
    total_cards_found: int
    best_match: Optional[CardRecommendation]
    reasoning: str
    execution_time: float


class BaseCardManager:
    """Base class for all card manager agents."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool, catalog_tool: CatalogTool):
        self.llm_tool = llm_tool
        self.policy_tool = policy_tool
        self.catalog_tool = catalog_tool
        self.manager_type = "base"
    
    async def analyze_request(self, request: RequestParsed) -> Dict[str, Any]:
        """Analyze the user request to understand requirements."""
        analysis_prompt = f"""
        Analyze this credit card request:
        Goals: {request.goals}
        Constraints: {request.constraints}
        Risk Tolerance: {request.risk_tolerance}
        Time Horizon: {request.time_horizon}
        
        Provide analysis in JSON format:
        {{
            "priority_categories": ["list of spending categories to focus on"],
            "reward_preferences": ["specific reward types preferred"],
            "constraint_analysis": "analysis of user constraints",
            "risk_assessment": "assessment of user's risk profile"
        }}
        """
        
        try:
            analysis = await self.llm_tool.nlu_extract(analysis_prompt, {})
            return analysis
        except Exception as e:
            # Fallback analysis
            return {
                "priority_categories": ["general"],
                "reward_preferences": request.goals,
                "constraint_analysis": f"Standard analysis for {request.risk_tolerance} risk",
                "risk_assessment": request.risk_tolerance
            }
    
    async def search_catalog(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search the card catalog based on criteria."""
        try:
            # Use catalog tool to search
            results = await self.catalog_tool.search_cards(criteria)
            return results
        except Exception as e:
            # Fallback to mock data
            return self._get_mock_cards()
    
    def _get_mock_cards(self) -> List[Dict[str, Any]]:
        """Fallback mock card data."""
        return [
            {
                "card_id": "mock_001",
                "card_name": "Mock Premium Card",
                "card_type": "rewards",
                "issuer": "Mock Bank",
                "annual_fee": 95.0,
                "rewards_rate": "2% on all purchases",
                "signup_bonus": "50,000 points",
                "credit_score_required": "excellent",
                "pros": ["High rewards rate", "Good signup bonus"],
                "cons": ["High annual fee", "Foreign transaction fees"]
            }
        ]
    
    async def rank_cards(self, cards: List[Dict[str, Any]], request: RequestParsed) -> List[CardRecommendation]:
        """Rank cards based on user preferences and requirements."""
        ranked_cards = []
        
        for card_data in cards:
            # Calculate match score based on goals and constraints
            match_score = self._calculate_match_score(card_data, request)
            
            # Create recommendation object
            recommendation = CardRecommendation(
                card_id=card_data["card_id"],
                card_name=card_data["card_name"],
                card_type=card_data["card_type"],
                issuer=card_data["issuer"],
                annual_fee=card_data["annual_fee"],
                rewards_rate=card_data["rewards_rate"],
                signup_bonus=card_data["signup_bonus"],
                credit_score_required=card_data["credit_score_required"],
                pros=card_data["pros"],
                cons=card_data["cons"],
                match_score=match_score,
                reasoning=self._generate_reasoning(card_data, request, match_score)
            )
            
            ranked_cards.append(recommendation)
        
        # Sort by match score (highest first)
        ranked_cards.sort(key=lambda x: x.match_score, reverse=True)
        return ranked_cards
    
    def _calculate_match_score(self, card: Dict[str, Any], request: RequestParsed) -> float:
        """Calculate how well a card matches user requirements."""
        score = 0.0
        
        # Goal matching (40% of score)
        goal_matches = sum(1 for goal in request.goals if goal.lower() in str(card).lower())
        score += (goal_matches / len(request.goals)) * 0.4 if request.goals else 0.0
        
        # Risk tolerance matching (30% of score)
        if request.risk_tolerance == "conservative" and card["annual_fee"] <= 50:
            score += 0.3
        elif request.risk_tolerance == "standard" and card["annual_fee"] <= 150:
            score += 0.3
        elif request.risk_tolerance == "aggressive":
            score += 0.3
        
        # Time horizon matching (20% of score)
        if request.time_horizon == "12m" and "signup_bonus" in str(card):
            score += 0.2
        
        # Constraint matching (10% of score)
        if not request.constraints:  # No constraints = flexible
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_reasoning(self, card: Dict[str, Any], request: RequestParsed, match_score: float) -> str:
        """Generate reasoning for why this card was recommended."""
        reasons = []
        
        if match_score > 0.8:
            reasons.append("Excellent match for your goals")
        elif match_score > 0.6:
            reasons.append("Good match for your preferences")
        elif match_score > 0.4:
            reasons.append("Moderate match, consider alternatives")
        else:
            reasons.append("Basic match, may not be optimal")
        
        if request.goals:
            goal_matches = [goal for goal in request.goals if goal.lower() in str(card).lower()]
            if goal_matches:
                reasons.append(f"Supports your goals: {', '.join(goal_matches)}")
        
        if card["annual_fee"] <= 50:
            reasons.append("Low annual fee")
        elif card["annual_fee"] <= 150:
            reasons.append("Moderate annual fee")
        else:
            reasons.append("Premium card with higher annual fee")
        
        return ". ".join(reasons)
    
    async def execute(self, state: GraphState) -> GraphState:
        """Execute the card manager agent."""
        import time
        start_time = time.time()
        
        try:
            # Update state
            state.current_node = self.manager_type
            state.completed_nodes.append(self.manager_type)
            
            # Analyze the request
            request = state.request
            analysis = await self.analyze_request(request)
            
            # Search for cards
            search_criteria = {
                "goals": request.goals,
                "risk_tolerance": request.risk_tolerance,
                "constraints": request.constraints,
                "jurisdiction": request.jurisdiction
            }
            
            raw_cards = await self.search_catalog(search_criteria)
            
            # Rank and filter cards
            recommendations = await self.rank_cards(raw_cards, request)
            
            # Take top 3 recommendations
            top_recommendations = recommendations[:3]
            
            # Create manager result
            manager_result = ManagerResult(
                manager_type=self.manager_type,
                recommendations=top_recommendations,
                total_cards_found=len(raw_cards),
                best_match=top_recommendations[0] if top_recommendations else None,
                reasoning=f"Found {len(raw_cards)} cards, ranked by relevance to your goals",
                execution_time=time.time() - start_time
            )
            
            # Update state
            state.manager_results[self.manager_type] = manager_result
            state.next_nodes = ["summary"]  # Next step is summary
            
            return state
            
        except Exception as e:
            # Handle errors gracefully
            error_info = {
                "node": self.manager_type,
                "error": str(e),
                "timestamp": time.time()
            }
            state.errors.append(error_info)
            state.next_nodes = ["summary"]  # Continue to summary even with errors
            return state


class TravelManager(BaseCardManager):
    """Manages travel-focused credit card recommendations."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool, catalog_tool: CatalogTool):
        super().__init__(llm_tool, policy_tool, catalog_tool)
        self.manager_type = "travel_manager"
    
    async def analyze_request(self, request: RequestParsed) -> Dict[str, Any]:
        """Specialized analysis for travel cards."""
        analysis = await super().analyze_request(request)
        
        # Add travel-specific analysis
        travel_goals = [goal for goal in request.goals if goal in ["miles", "travel", "airline", "hotel"]]
        analysis["travel_specific"] = {
            "airline_preferences": "any" if "airline" in travel_goals else "none",
            "hotel_preferences": "any" if "hotel" in travel_goals else "none",
            "international_travel": "yes" if request.jurisdiction != "US" else "maybe"
        }
        
        return analysis
    
    def _calculate_match_score(self, card: Dict[str, Any], request: RequestParsed) -> float:
        """Enhanced scoring for travel cards."""
        base_score = super()._calculate_match_score(card, request)
        
        # Boost travel-specific features
        card_text = str(card).lower()
        if any(word in card_text for word in ["miles", "airline", "travel"]):
            base_score += 0.2
        
        if "no foreign transaction fee" in card_text:
            base_score += 0.1
        
        return min(base_score, 1.0)


class CashbackManager(BaseCardManager):
    """Manages cashback-focused credit card recommendations."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool, catalog_tool: CatalogTool):
        super().__init__(llm_tool, policy_tool, catalog_tool)
        self.manager_type = "cashback_manager"
    
    async def analyze_request(self, request: RequestParsed) -> Dict[str, Any]:
        """Specialized analysis for cashback cards."""
        analysis = await super().analyze_request(request)
        
        # Add cashback-specific analysis
        analysis["cashback_specific"] = {
            "category_preferences": "flexible" if "general" in request.goals else "specific",
            "quarterly_rotations": "yes" if "rotating" in request.goals else "no",
            "flat_rate_preferred": "yes" if "simple" in request.goals else "no"
        }
        
        return analysis
    
    def _calculate_match_score(self, card: Dict[str, Any], request: RequestParsed) -> float:
        """Enhanced scoring for cashback cards."""
        base_score = super()._calculate_match_score(card, request)
        
        # Boost cashback-specific features
        card_text = str(card).lower()
        if "cashback" in card_text:
            base_score += 0.2
        
        if "%" in str(card.get("rewards_rate", "")):
            base_score += 0.1
        
        return min(base_score, 1.0)


class BusinessManager(BaseCardManager):
    """Manages business-focused credit card recommendations."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool, catalog_tool: CatalogTool):
        super().__init__(llm_tool, policy_tool, catalog_tool)
        self.manager_type = "business_manager"
    
    async def analyze_request(self, request: RequestParsed) -> Dict[str, Any]:
        """Specialized analysis for business cards."""
        analysis = await super().analyze_request(request)
        
        # Add business-specific analysis
        analysis["business_specific"] = {
            "expense_categories": ["office_supplies", "travel", "dining"],
            "employee_cards": "yes" if "employee" in request.goals else "no",
            "expense_tracking": "required" if "tracking" in request.goals else "optional"
        }
        
        return analysis


class StudentManager(BaseCardManager):
    """Manages student-focused credit card recommendations."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool, catalog_tool: CatalogTool):
        super().__init__(llm_tool, policy_tool, catalog_tool)
        self.manager_type = "student_manager"
    
    async def analyze_request(self, request: RequestParsed) -> Dict[str, Any]:
        """Specialized analysis for student cards."""
        analysis = await super().analyze_request(request)
        
        # Add student-specific analysis
        analysis["student_specific"] = {
            "credit_building": "primary" if "building_credit" in request.goals else "secondary",
            "income_requirements": "low" if "student" in request.goals else "standard",
            "educational_benefits": "yes" if "student" in request.goals else "no"
        }
        
        return analysis
    
    def _calculate_match_score(self, card: Dict[str, Any], request: RequestParsed) -> float:
        """Enhanced scoring for student cards."""
        base_score = super()._calculate_match_score(card, request)
        
        # Boost student-friendly features
        card_text = str(card).lower()
        if "student" in card_text or "first" in card_text:
            base_score += 0.3
        
        if card.get("annual_fee", 1000) <= 0:
            base_score += 0.2
        
        return min(base_score, 1.0)


class GeneralManager(BaseCardManager):
    """Manages general-purpose credit card recommendations."""
    
    def __init__(self, llm_tool: LLMTool, policy_tool: PolicyTool, catalog_tool: CatalogTool):
        super().__init__(llm_tool, policy_tool, catalog_tool)
        self.manager_type = "general_manager"
    
    async def analyze_request(self, request: RequestParsed) -> Dict[str, Any]:
        """General analysis for all-purpose cards."""
        analysis = await super().analyze_request(request)
        
        # Add general-purpose analysis
        analysis["general_specific"] = {
            "flexibility": "high",
            "category_agnostic": "yes",
            "suitable_for": "daily_use"
        }
        
        return analysis


# Factory function to create card manager nodes
def create_card_manager_node(manager_class: type) -> callable:
    """Create a LangGraph-compatible node for a card manager."""
    
    async def card_manager_node(state: GraphState) -> GraphState:
        """LangGraph node function for card manager execution."""
        # Create manager instance (we'll need to pass tools)
        # For now, create mock tools
        from src.tools.mock_tools import MockLLMTool, MockPolicyTool, MockCatalogTool
        
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        mock_catalog = MockCatalogTool()
        
        manager = manager_class(mock_llm, mock_policy, mock_catalog)
        
        # Execute the manager
        return await manager.execute(state)
    
    return card_manager_node


# Specific node creators
def create_travel_manager_node():
    return create_card_manager_node(TravelManager)

def create_cashback_manager_node():
    return create_card_manager_node(CashbackManager)

def create_business_manager_node():
    return create_card_manager_node(BusinessManager)

def create_student_manager_node():
    return create_card_manager_node(StudentManager)

def create_general_manager_node():
    return create_card_manager_node(GeneralManager)
