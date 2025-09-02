"""
OpenAI LLM Tool Implementation
Real LLM integration for the Credit Card Recommendation Agent
"""

import json
import logging
from typing import Dict, Any, List
import openai
from openai import AsyncOpenAI

from src.tools.base import LLMTool


logger = logging.getLogger(__name__)


class OpenAILLMTool(LLMTool):
    """
    Real OpenAI LLM tool for structured data extraction and explanation generation.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI LLM tool.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.node_name = "openai_llm_tool"
    
    async def execute(self, **kwargs):
        """Implement abstract method."""
        pass
    
    async def nlu_extract(self, text: str, schema: dict) -> Dict[str, Any]:
        """
        Extract structured data from text using OpenAI.
        
        Args:
            text: Raw user query
            schema: JSON schema for extraction
            
        Returns:
            Structured data matching the schema
        """
        try:
            # Create a detailed prompt for extraction
            system_prompt = f"""
You are a credit card recommendation specialist. Extract structured information from user queries.

Extract ONLY the information that is explicitly mentioned or can be reasonably inferred from the query.
Do NOT make assumptions beyond what is stated or implied.

Return a valid JSON object that matches this schema:
{json.dumps(schema, indent=2)}

Rules:
- Set jurisdiction to "SG" unless explicitly specified otherwise
- Only include fields that have actual values
- For constraints, use reasonable defaults if ranges are mentioned
- For goals, identify the primary intent (miles, cashback, rewards, travel, business, student)
- Set confidence based on how clear and specific the query is (0.5 to 1.0)
"""

            user_prompt = f"User query: {text}\n\nExtract the structured information:"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            logger.info(f"OpenAI extraction successful for query: {text[:50]}...")
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            # Fallback to basic extraction
            return self._fallback_extraction(text, schema)
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            # Fallback to basic extraction
            return self._fallback_extraction(text, schema)
    
    async def explainer(self, card_list: List[Any], request: Dict[str, Any]) -> str:
        """
        Generate user-friendly explanations using OpenAI.
        
        Args:
            card_list: List of recommended cards
            request: Original user request
            
        Returns:
            Natural language explanation
        """
        try:
            # Create a prompt for explanation generation
            system_prompt = """
You are a helpful credit card advisor. Explain the recommendations in a clear, friendly way.

Focus on:
- Why these cards match the user's needs
- Key benefits and features
- Any important considerations or trade-offs
- Next steps for the user

Keep explanations concise but informative (2-3 sentences per card).
"""

            user_prompt = f"""
User request: {json.dumps(request, indent=2)}

Recommended cards: {json.dumps([card.dict() if hasattr(card, 'dict') else card for card in card_list], indent=2)}

Please explain why these cards are recommended for this user.
"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Slightly higher for more natural explanations
                max_tokens=500
            )
            
            explanation = response.choices[0].message.content
            logger.info("OpenAI explanation generation successful")
            return explanation
            
        except Exception as e:
            logger.error(f"OpenAI explanation generation failed: {str(e)}")
            # Fallback to basic explanation
            return self._fallback_explanation(card_list, request)
    
    def _fallback_extraction(self, text: str, schema: dict) -> Dict[str, Any]:
        """
        Fallback extraction when OpenAI fails.
        
        Args:
            text: Raw user query
            schema: JSON schema for extraction
            
        Returns:
            Basic extracted data
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
        if any(word in text_lower for word in ["business", "corporate", "expenses"]):
            goals.append("business_expenses")
        if any(word in text_lower for word in ["student", "college", "university"]):
            goals.append("student")
        
        # Basic constraints
        constraints = {}
        if "no fee" in text_lower or "no annual fee" in text_lower:
            constraints["annual_fee_max"] = 0
        elif "low fee" in text_lower or "cheap" in text_lower:
            constraints["annual_fee_max"] = 100
        
        # Default values
        return {
            "intent": "recommend_card",
            "goals": goals if goals else ["rewards"],
            "constraints": constraints,
            "jurisdiction": "SG",
            "risk_tolerance": "standard",
            "time_horizon": "12m",
            "confidence": 0.5  # Lower confidence for fallback
        }
    
    def _fallback_explanation(self, card_list: List[Any], request: Dict[str, Any]) -> str:
        """
        Fallback explanation when OpenAI fails.
        
        Args:
            card_list: List of recommended cards
            request: Original user request
            
        Returns:
            Basic explanation
        """
        if not card_list:
            return "I couldn't find any cards matching your requirements. Please try adjusting your criteria."
        
        card_names = [getattr(card, 'card_id', str(card)) for card in card_list]
        
        return f"I found {len(card_list)} card(s) that match your needs: {', '.join(card_names[:3])}. These cards align with your goals of {', '.join(request.get('goals', ['rewards']))}."

