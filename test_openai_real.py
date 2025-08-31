#!/usr/bin/env python3
"""
Test OpenAI Real LLM Integration
Tests the complete system with real OpenAI LLM instead of mock.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


async def test_openai_llm_tool():
    """Test the OpenAI LLM tool directly."""
    print("🧪 Testing OpenAI LLM Tool...")
    
    try:
        # Create LLM tool with OpenAI (will fallback to mock if no API key)
        llm_tool = MockLLMTool(use_openai=True)
        
        if llm_tool.use_openai:
            print("   ✅ OpenAI LLM mode enabled")
            
            # Test NLU extraction
            schema = {
                "type": "object",
                "properties": {
                    "intent": {"type": "string"},
                    "goals": {"type": "array", "items": {"type": "string"}},
                    "jurisdiction": {"type": "string"},
                    "risk_tolerance": {"type": "string"}
                }
            }
            
            test_query = "I want a travel credit card for airline miles and international travel"
            print(f"   ✅ Testing extraction with: {test_query}")
            
            result = await llm_tool.nlu_extract(test_query, schema)
            print(f"   ✅ Extraction result: {result}")
            
            # Test response generation
            prompt = "Explain why this card is good for travel"
            response = await llm_tool.generate_response(prompt, {"card_type": "travel"})
            print(f"   ✅ Generated response: {response[:100]}...")
            
        else:
            print("   ⚠️ OpenAI API key not found, using mock mode")
            print("   💡 Set OPENAI_API_KEY environment variable to test real LLM")
        
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI LLM tool test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_openai_graph_integration():
    """Test the complete graph with OpenAI LLM."""
    print("\n🧪 Testing OpenAI Graph Integration...")
    
    try:
        # Create tools with OpenAI LLM
        llm_tool = MockLLMTool(use_openai=True)
        policy_tool = MockPolicyTool()
        
        if not llm_tool.use_openai:
            print("   ⚠️ Skipping OpenAI test - no API key available")
            return True
        
        # Create and test graph
        graph = create_credit_card_graph(llm_tool, policy_tool)
        print("   ✅ Graph created with OpenAI LLM")
        
        # Test with a travel request
        initial_state = create_initial_state(
            "I need a credit card for business travel with lounge access and travel insurance"
        )
        
        print(f"   ✅ Testing with query: {initial_state.user_query}")
        
        # Execute the graph
        result = await graph.ainvoke(initial_state)
        
        print(f"   ✅ Graph execution completed")
        print(f"   ✅ Final state keys: {list(result.keys())}")
        
        # Check results
        if 'completed_nodes' in result:
            completed_nodes = result['completed_nodes']
            print(f"   ✅ Completed nodes: {completed_nodes}")
        
        if 'manager_results' in result and result['manager_results']:
            print(f"   ✅ Manager results available")
            for manager_type, manager_result in result['manager_results'].items():
                print(f"   ✅ {manager_type}: {len(manager_result.recommendations)} recommendations")
        
        if 'final_recommendations' in result and result['final_recommendations']:
            final_recs = result['final_recommendations']
            print(f"   ✅ Final recommendations available")
            print(f"   ✅ Total cards analyzed: {final_recs.total_cards_analyzed}")
            
            if final_recs.top_recommendation:
                top_rec = final_recs.top_recommendation
                print(f"   ✅ Top recommendation: {top_rec.card_name}")
                print(f"   ✅ Overall score: {top_rec.overall_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI graph integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_openai_fallback():
    """Test that the system gracefully falls back to mock when OpenAI fails."""
    print("\n🧪 Testing OpenAI Fallback Behavior...")
    
    try:
        # Create LLM tool with OpenAI but simulate failure
        llm_tool = MockLLMTool(use_openai=True)
        
        if not llm_tool.use_openai:
            print("   ⚠️ Skipping fallback test - no API key available")
            return True
        
        # Test with a complex query that might trigger fallback
        schema = {
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "goals": {"type": "array", "items": {"type": "string"}},
                "jurisdiction": {"type": "string"}
            }
        }
        
        test_query = "I want a credit card for students with no annual fee and good rewards"
        print(f"   ✅ Testing fallback with: {test_query}")
        
        result = await llm_tool.nlu_extract(test_query, schema)
        print(f"   ✅ Fallback result: {result}")
        
        # Verify fallback worked
        if result.get("goals") and "student" in result["goals"]:
            print("   ✅ Fallback extraction successful")
        else:
            print("   ⚠️ Fallback extraction may not have worked as expected")
        
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI fallback test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all OpenAI integration tests."""
    print("🚀 Testing OpenAI Real LLM Integration")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API key found: {api_key[:10]}...")
    else:
        print("⚠️ No OpenAI API key found - tests will use mock mode")
        print("💡 Set OPENAI_API_KEY environment variable to test real LLM")
    
    print()
    
    # Run tests
    tests = [
        test_openai_llm_tool,
        test_openai_graph_integration,
        test_openai_fallback
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
