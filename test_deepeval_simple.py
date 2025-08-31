#!/usr/bin/env python3
"""
Simple DeepEval Test
Quick validation of the credit card recommendation system using DeepEval.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, AnswerCorrectnessMetric
from deepeval.test_case import LLMTestCase
from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


async def test_simple_deepeval():
    """Simple DeepEval test with basic metrics."""
    print("🧪 Simple DeepEval Test...")
    
    # Create a simple test case
    test_case = LLMTestCase(
        input="I want a travel credit card for airline miles",
        expected_output="Should recommend travel credit cards with airline miles",
        context="User wants travel-focused credit card"
    )
    
    try:
        # Create tools and graph
        llm_tool = MockLLMTool(use_openai=True)
        policy_tool = MockPolicyTool()
        graph = create_credit_card_graph(llm_tool, policy_tool)
        
        # Execute the graph
        initial_state = create_initial_state(test_case.input)
        result = await graph.ainvoke(initial_state)
        
        # Extract response
        if 'final_recommendations' in result and result['final_recommendations']:
            final_recs = result['final_recommendations']
            response = f"Recommended {len(final_recs.final_recommendations)} travel credit cards. Top choice: {final_recs.top_recommendation.card_name if final_recs.top_recommendation else 'None'}"
        else:
            response = "No recommendations generated"
        
        print(f"   ✅ Input: {test_case.input}")
        print(f"   ✅ Response: {response}")
        
        # Evaluate using DeepEval
        test_result = evaluate(
            test_case,
            response,
            metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
        )
        
        print(f"   ✅ DeepEval Score: {test_result.score:.3f}")
        return test_result
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return None


async def test_multiple_scenarios():
    """Test multiple scenarios with DeepEval."""
    print("\n🧪 Testing Multiple Scenarios...")
    
    test_cases = [
        LLMTestCase(
            input="I need a cashback credit card for groceries",
            expected_output="Should recommend cashback credit cards for groceries",
            context="User wants cashback card for grocery spending"
        ),
        LLMTestCase(
            input="Looking for a business credit card",
            expected_output="Should recommend business credit cards",
            context="User wants business credit card"
        )
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            # Create tools and graph
            llm_tool = MockLLMTool(use_openai=True)
            policy_tool = MockPolicyTool()
            graph = create_credit_card_graph(llm_tool, policy_tool)
            
            # Execute the graph
            initial_state = create_initial_state(test_case.input)
            result = await graph.ainvoke(initial_state)
            
            # Extract response
            if 'final_recommendations' in result and result['final_recommendations']:
                final_recs = result['final_recommendations']
                response = f"Generated {len(final_recs.final_recommendations)} recommendations"
            else:
                response = "No recommendations generated"
            
            print(f"   ✅ {test_case.input[:40]}... - {response}")
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
            )
            
            results.append(test_result)
            print(f"   📊 Score: {test_result.score:.3f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def main():
    """Run simple DeepEval tests."""
    print("🚀 Simple DeepEval Testing")
    print("=" * 40)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API key found: {api_key[:10]}...")
    else:
        print("⚠️ No OpenAI API key found - tests will use mock mode")
    
    print()
    
    # Run simple test
    simple_result = await test_simple_deepeval()
    
    # Run multiple scenarios
    scenario_results = await test_multiple_scenarios()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 DeepEval Test Summary")
    print("=" * 40)
    
    all_results = [simple_result] + scenario_results if simple_result else scenario_results
    all_results = [r for r in all_results if r is not None]
    
    if all_results:
        total_tests = len(all_results)
        avg_score = sum(result.score for result in all_results) / total_tests
        
        print(f"✅ Total Tests: {total_tests}")
        print(f"📊 Average Score: {avg_score:.3f}")
        
        if avg_score >= 0.8:
            print("🎉 Excellent performance!")
        elif avg_score >= 0.6:
            print("✅ Good performance!")
        else:
            print("⚠️ Performance needs improvement")
    
    return all_results


if __name__ == "__main__":
    asyncio.run(main())
