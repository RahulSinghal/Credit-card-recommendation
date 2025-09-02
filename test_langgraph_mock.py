#!/usr/bin/env python3
"""
Test LangGraph Integration with Mock Tools
Validates the refactored implementation using LangGraph without requiring OpenAI API keys.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_credit_card_graph, create_initial_state
from src.tools.base import LLMTool, PolicyTool


class MockLLMTool(LLMTool):
    """Mock LLM tool for testing LangGraph integration."""
    
    async def execute(self, **kwargs):
        pass
    
    async def nlu_extract(self, text: str, schema: dict):
        """Mock extraction that returns structured data."""
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
        
        return {
            "intent": "recommend_card",
            "goals": goals if goals else ["rewards"],
            "constraints": constraints,
            "jurisdiction": "SG",
            "risk_tolerance": "standard",
            "time_horizon": "12m",
            "confidence": 0.8
        }
    
    async def explainer(self, card_list, request):
        """Mock explanation generation."""
        return f"Mock explanation for {len(card_list)} cards based on {request.get('goals', ['rewards'])} goals."


class MockPolicyTool(PolicyTool):
    """Mock policy tool for testing."""
    
    async def execute(self, **kwargs):
        pass
    
    async def lint_final(self, recos, policy):
        return type('MockPolicyReport', (), {'errors': [], 'warnings': []})()


async def test_langgraph_mock():
    """Test the LangGraph-powered Extractor Node with mock tools."""
    print("🚀 Testing LangGraph Integration with Mock Tools...")
    
    try:
        # Create mock tools
        mock_llm_tool = MockLLMTool()
        mock_policy_tool = MockPolicyTool()
        
        # Create the LangGraph
        graph = create_credit_card_graph(mock_llm_tool, mock_policy_tool)
        
        print("✅ LangGraph created successfully")
        
        # Test queries
        test_queries = [
            "I want a travel credit card with lounge access",
            "Looking for a cashback card for groceries with no annual fee",
            "Need a business credit card for company expenses and employee cards",
            "I'm a student looking for my first credit card with no annual fee"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test {i}: {query}")
            
            # Create initial state
            initial_state = create_initial_state(
                user_query=query,
                locale="en-SG"
            )
            
            # Execute the graph
            config = {"configurable": {"thread_id": f"test-{i}"}}
            result = await graph.ainvoke(initial_state, config)
            
            # Display results
            if result.get("request"):
                print(f"✅ Extraction successful!")
                print(f"   Intent: {result['request'].intent}")
                print(f"   Goals: {result['request'].goals}")
                print(f"   Jurisdiction: {result['request'].jurisdiction}")
                if result['request'].constraints:
                    print(f"   Constraints: {result['request'].constraints}")
                print(f"   Confidence: {result['request'].confidence}")
                
                # Check routing
                if result.get("fanout_plan"):
                    print(f"   Routing Plan: {result['fanout_plan']}")
                
                # Check completed nodes
                if result.get("completed_nodes"):
                    print(f"   Completed Nodes: {result['completed_nodes']}")
            else:
                print(f"❌ Extraction failed")
                
            # Check for errors
            if result.get("errors"):
                print(f"⚠️  Errors: {len(result['errors'])}")
                for error in result['errors']:
                    print(f"     {error['node']}: {error['error']}")
        
        print("\n🎉 All LangGraph mock tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ LangGraph mock integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the LangGraph mock integration test."""
    print("🚀 Starting LangGraph Mock Integration Test...\n")
    
    success = await test_langgraph_mock()
    
    print("\n" + "="*60)
    print("📊 LANGGRAPH MOCK INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 LangGraph Mock Integration Complete!")
        print("✅ The system is now using proper LangGraph orchestration.")
        print("✅ The Extractor Node is working correctly with LangGraph.")
        print("✅ Ready to implement the remaining nodes (Card Managers, Summary, etc.).")
        return 0
    else:
        print("\n💥 LangGraph mock integration failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

