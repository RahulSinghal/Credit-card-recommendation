#!/usr/bin/env python3
"""
Debug LangGraph Integration
Simple step-by-step test to identify issues.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def debug_langgraph():
    """Debug LangGraph step by step."""
    print("🔍 Debugging LangGraph Integration...")
    
    try:
        # Step 1: Import modules
        print("✅ Step 1: Importing modules...")
        from src.tools.base import LLMTool, PolicyTool
        from src.graph import create_credit_card_graph
        print("   ✅ All modules imported successfully")
        
        # Step 2: Create mock tools
        print("✅ Step 2: Creating mock tools...")
        
        class MockLLMTool(LLMTool):
            async def execute(self, **kwargs):
                pass
            async def nlu_extract(self, text: str, schema: dict):
                return {
                    "intent": "recommend_card",
                    "goals": ["rewards"],
                    "constraints": {},
                    "jurisdiction": "SG",
                    "risk_tolerance": "standard",
                    "time_horizon": "12m",
                    "confidence": 0.8
                }
            async def explainer(self, card_list, request):
                return "Mock explanation"
        
        class MockPolicyTool(PolicyTool):
            async def execute(self, **kwargs):
                pass
            async def lint_final(self, recos, policy):
                return type('MockPolicyReport', (), {'errors': [], 'warnings': []})()
        
        mock_llm_tool = MockLLMTool()
        mock_policy_tool = MockPolicyTool()
        print("   ✅ Mock tools created successfully")
        
        # Step 3: Create graph
        print("✅ Step 3: Creating LangGraph...")
        graph = create_credit_card_graph(mock_llm_tool, mock_policy_tool)
        print("   ✅ LangGraph created successfully")
        
        # Step 4: Test graph execution
        print("✅ Step 4: Testing graph execution...")
        from src.graph import create_initial_state
        
        initial_state = create_initial_state(
            user_query="I want a travel credit card",
            locale="en-SG"
        )
        
        config = {"configurable": {"thread_id": "debug-test"}}
        result = await graph.ainvoke(initial_state, config)
        
        print("   ✅ Graph execution successful!")
        print(f"   📊 Result keys: {list(result.keys())}")
        
        if result.get("request"):
            print(f"   🎯 Request extracted: {result['request'].intent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed at step: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_langgraph())
    print(f"\n🎯 Debug {'SUCCESSFUL' if success else 'FAILED'}")

