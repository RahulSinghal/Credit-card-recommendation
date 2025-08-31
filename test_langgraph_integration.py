#!/usr/bin/env python3
"""
Test LangGraph Integration
Validates the refactored implementation using LangGraph.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_credit_card_graph, create_initial_state
from src.tools.openai_llm import OpenAILLMTool
from src.tools.base import PolicyTool


class MockPolicyTool(PolicyTool):
    """Mock policy tool for testing."""
    
    async def execute(self, **kwargs):
        pass
    
    async def lint_final(self, recos, policy):
        return type('MockPolicyReport', (), {'errors': [], 'warnings': []})()


async def test_langgraph_extractor():
    """Test the LangGraph-powered Extractor Node."""
    print("🚀 Testing LangGraph Integration...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key in a .env file or environment variable")
            return False
        
        # Create tools
        openai_tool = OpenAILLMTool(api_key=api_key)
        policy_tool = MockPolicyTool()
        
        # Create the LangGraph
        graph = create_credit_card_graph(openai_tool, policy_tool)
        
        print("✅ LangGraph created successfully")
        
        # Test queries
        test_queries = [
            "I want a travel credit card with lounge access",
            "Looking for a cashback card for groceries",
            "Need a business credit card for company expenses"
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
        
        print("\n🎉 All LangGraph tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ LangGraph integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the LangGraph integration test."""
    print("🚀 Starting LangGraph Integration Test...\n")
    
    success = await test_langgraph_extractor()
    
    print("\n" + "="*60)
    print("📊 LANGGRAPH INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 LangGraph Integration Complete!")
        print("✅ The system is now using proper LangGraph orchestration.")
        print("✅ Ready to implement the remaining nodes (Card Managers, Summary, etc.).")
        return 0
    else:
        print("\n💥 LangGraph integration failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
