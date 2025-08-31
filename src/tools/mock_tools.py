#!/usr/bin/env python3
"""
Credit Card Recommendation Tools
Provides implementations of all tool interfaces with OpenAI LLM integration.
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from src.tools.base import LLMTool, PolicyTool, CatalogTool

# Load environment variables from .env file
load_dotenv()


class MockLLMTool(LLMTool):
    """LLM tool using OpenAI for production, with fallback to mock for testing."""
    
    def __init__(self, use_openai: bool = True, api_key: str = None, model: str = "gpt-4o-mini"):
        """Initialize with option to use OpenAI or fallback to mock."""
        self.use_openai = use_openai
        if use_openai:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("Warning: No OpenAI API key found, falling back to mock mode")
                self.use_openai = False
            else:
                self.model = model
                self.client = AsyncOpenAI(api_key=self.api_key)
        
        if not self.use_openai:
            print("Using mock LLM mode")
    
    async def execute(self, **kwargs):
        """Required abstract method implementation."""
        pass
    
    async def nlu_extract(self, text: str, schema: dict) -> Dict[str, Any]:
        """Extract structured information using OpenAI LLM or fallback to keyword matching."""
        if self.use_openai:
            try:
                # Create a detailed prompt for extraction
                prompt = f"""
                Analyze the following user query and extract structured information according to the schema.
                
                User Query: {text}
                
                Schema: {json.dumps(schema, indent=2)}
                
                Please extract the information and return ONLY a valid JSON object that matches the schema.
                Be precise and accurate in your extraction.
                """
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise information extraction assistant. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                # Extract and parse the response
                content = response.choices[0].message.content.strip()
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON content between ```json and ``` markers
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        if json_end != -1:
                            content = content[json_start:json_end].strip()
                    
                    # Parse the JSON
                    result = json.loads(content)
                    
                    # Validate and normalize goals
                    if "goals" in result:
                        if not isinstance(result["goals"], list):
                            result["goals"] = [result["goals"]] if result["goals"] else []
                        
                        # Map common variations to standard goals
                        goal_mapping = {
                            "miles": "miles", "travel": "miles", "airline": "miles",
                            "cashback": "cashback", "cash": "cashback", "money": "cashback",
                            "business": "business", "corporate": "business", "expense": "business",
                            "student": "student", "college": "student", "university": "student",
                            "credit": "building_credit", "building": "building_credit", "first": "building_credit"
                        }
                        
                        mapped_goals = []
                        for goal in result["goals"]:
                            goal_lower = goal.lower()
                            mapped_goal = goal_mapping.get(goal_lower, goal_lower)
                            if mapped_goal not in mapped_goals:
                                mapped_goals.append(mapped_goal)
                        
                        result["goals"] = mapped_goals
                    
                    return result
                    
                except json.JSONDecodeError:
                    print("OpenAI response parsing failed, falling back to keyword extraction")
                    return await self._fallback_extraction(text, schema)
                    
            except Exception as e:
                print(f"OpenAI extraction failed: {e}, falling back to keyword extraction")
                return await self._fallback_extraction(text, schema)
        
        # Fallback to keyword-based extraction
        return await self._fallback_extraction(text, schema)
    
    async def _fallback_extraction(self, text: str, schema: dict) -> Dict[str, Any]:
        """Fallback extraction using keyword matching."""
        text_lower = text.lower()
        
        # Basic keyword extraction
        goals = []
        if any(word in text_lower for word in ["miles", "travel", "airline"]):
            goals.extend(["miles", "travel"])
        if any(word in text_lower for word in ["cashback", "cash", "money"]):
            goals.append("cashback")
        if any(word in text_lower for word in ["business", "corporate", "expense"]):
            goals.append("business")
        if any(word in text_lower for word in ["student", "college", "university"]):
            goals.append("student")
        if any(word in text_lower for word in ["credit", "building", "first"]):
            goals.append("building_credit")
        
        # Default goals if none found
        if not goals:
            goals = ["rewards"]
        
        return {
            "intent": "recommend_card",
            "goals": goals,
            "constraints": {},
            "jurisdiction": "SG",
            "risk_tolerance": "standard",
            "time_horizon": "12m",
            "confidence": 0.6  # Lower confidence for fallback
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using OpenAI LLM or fallback to mock."""
        if self.use_openai:
            try:
                # Build the full prompt with context
                full_prompt = prompt
                if context:
                    context_str = json.dumps(context, indent=2)
                    full_prompt = f"Context: {context_str}\n\nPrompt: {prompt}"
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful credit card recommendation assistant."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"OpenAI response generation failed: {e}, falling back to mock")
                return f"Mock response to: {prompt[:50]}..."
        
        # Fallback to mock response
        return f"Mock response to: {prompt[:50]}..."


class MockPolicyTool(PolicyTool):
    """Mock policy tool for testing."""
    
    async def execute(self, **kwargs):
        """Required abstract method implementation."""
        pass
    
    async def get_policy_pack(self, jurisdiction: str, locale: str) -> Dict[str, Any]:
        """Mock policy pack retrieval."""
        return {
            "jurisdiction": jurisdiction,
            "locale": locale,
            "regulations": {
                "credit_pull": "soft_only",
                "data_sharing": "minimal",
                "consent_required": True
            },
            "compliance": {
                "gdpr": True if locale.startswith("en-") else False,
                "ccpa": True if jurisdiction == "US" else False
            }
        }
    
    async def validate_request(self, request: Dict[str, Any], policy_pack: Dict[str, Any]) -> Dict[str, Any]:
        """Mock request validation."""
        return {
            "valid": True,
            "warnings": [],
            "required_consent": ["personalization", "data_sharing"]
        }


class MockCatalogTool(CatalogTool):
    """Mock catalog tool for testing."""
    
    async def execute(self, **kwargs):
        """Required abstract method implementation."""
        pass
    
    async def search_cards(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock card search with realistic data."""
        # Generate mock cards based on criteria
        mock_cards = []
        
        goals = criteria.get("goals", [])
        risk_tolerance = criteria.get("risk_tolerance", "standard")
        jurisdiction = criteria.get("jurisdiction", "SG")
        
        # Travel cards
        if any(goal in goals for goal in ["miles", "travel", "airline"]):
            mock_cards.extend([
                {
                    "card_id": "travel_001",
                    "card_name": "Singapore Airlines KrisFlyer Credit Card",
                    "card_type": "travel",
                    "issuer": "DBS Bank",
                    "annual_fee": 192.60,
                    "rewards_rate": "1.2 miles per S$1",
                    "signup_bonus": "15,000 KrisFlyer miles",
                    "credit_score_required": "excellent",
                    "pros": ["High miles earning", "No foreign transaction fees", "Travel insurance"],
                    "cons": ["High annual fee", "Limited cashback options"]
                },
                {
                    "card_id": "travel_002",
                    "card_name": "Citi PremierMiles Card",
                    "card_type": "travel",
                    "issuer": "Citibank",
                    "annual_fee": 192.60,
                    "rewards_rate": "1.2 miles per S$1",
                    "signup_bonus": "10,000 miles",
                    "credit_score_required": "good",
                    "pros": ["Flexible miles", "Good signup bonus", "Travel benefits"],
                    "cons": ["Annual fee", "Limited category bonuses"]
                }
            ])
        
        # Cashback cards
        if any(goal in goals for goal in ["cashback", "rewards"]):
            mock_cards.extend([
                {
                    "card_id": "cashback_001",
                    "card_name": "DBS Live Fresh Card",
                    "card_type": "cashback",
                    "issuer": "DBS Bank",
                    "annual_fee": 0,
                    "rewards_rate": "5% cashback on online spending",
                    "signup_bonus": "S$100 cashback",
                    "credit_score_required": "good",
                    "pros": ["No annual fee", "High online cashback", "Easy to use"],
                    "cons": ["Limited offline benefits", "Category restrictions"]
                },
                {
                    "card_id": "cashback_002",
                    "card_name": "OCBC 365 Credit Card",
                    "card_type": "cashback",
                    "issuer": "OCBC Bank",
                    "annual_fee": 0,
                    "rewards_rate": "6% cashback on dining",
                    "signup_bonus": "S$80 cashback",
                    "credit_score_required": "good",
                    "pros": ["No annual fee", "High dining cashback", "Weekend bonuses"],
                    "cons": ["Complex bonus structure", "Minimum spending requirements"]
                }
            ])
        
        # Business cards
        if any(goal in goals for goal in ["business", "corporate"]):
            mock_cards.extend([
                {
                    "card_id": "business_001",
                    "card_name": "UOB Business Card",
                    "card_type": "business",
                    "issuer": "UOB Bank",
                    "annual_fee": 96.30,
                    "rewards_rate": "1% cashback on all spending",
                    "signup_bonus": "S$200 cashback",
                    "credit_score_required": "good",
                    "pros": ["Business expense tracking", "Employee cards", "Corporate benefits"],
                    "cons": ["Annual fee", "Limited rewards", "Business verification required"]
                }
            ])
        
        # Student cards
        if any(goal in goals for goal in ["student", "building_credit"]):
            mock_cards.extend([
                {
                    "card_id": "student_001",
                    "card_name": "POSB Everyday Card",
                    "card_type": "student",
                    "issuer": "DBS Bank",
                    "annual_fee": 0,
                    "rewards_rate": "0.3% cashback on all spending",
                    "signup_bonus": "S$20 cashback",
                    "credit_score_required": "fair",
                    "pros": ["No annual fee", "Easy approval", "Credit building"],
                    "cons": ["Low rewards rate", "Limited benefits", "Low credit limit"]
                }
            ])
        
        # General cards (fallback)
        if not mock_cards:
            mock_cards.append({
                "card_id": "general_001",
                "card_name": "Standard Rewards Card",
                "card_type": "rewards",
                "issuer": "Generic Bank",
                "annual_fee": 48.15,
                "rewards_rate": "1% cashback on all spending",
                "signup_bonus": "S$50 cashback",
                "credit_score_required": "good",
                "pros": ["Simple rewards", "Moderate annual fee", "Widely accepted"],
                "cons": ["Basic benefits", "No category bonuses", "Limited perks"]
            })
        
        # Filter by risk tolerance
        if risk_tolerance == "conservative":
            mock_cards = [card for card in mock_cards if card["annual_fee"] <= 50]
        elif risk_tolerance == "standard":
            mock_cards = [card for card in mock_cards if card["annual_fee"] <= 200]
        # Aggressive risk accepts all cards
        
        return mock_cards[:5]  # Return max 5 cards
    
    async def get_card_details(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Mock detailed card information."""
        # This would normally fetch detailed info from a database
        return {
            "card_id": card_id,
            "detailed_info": "Mock detailed information for testing",
            "terms_conditions": "Mock terms and conditions",
            "fees": "Mock fee structure"
        }
    
    async def get_card_categories(self) -> List[str]:
        """Mock card categories."""
        return [
            "travel", "cashback", "business", "student", 
            "rewards", "balance_transfer", "secured", "premium"
        ]
