#!/usr/bin/env python3
"""
Simplified DeepEval Test for Credit Card Recommendation System
Tests individual nodes and the whole system using available DeepEval metrics.
"""

import asyncio
import sys
import os
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, AnswerCorrectnessMetric
from deepeval.test_case import LLMTestCase
from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


class CreditCardRelevancyMetric:
    """Custom metric for credit card recommendation relevancy."""
    
    def __init__(self):
        self.name = "CreditCardRelevancy"
    
    def measure(self, test_case: LLMTestCase, response: str) -> float:
        """Measure how relevant the credit card recommendation is."""
        score = 0.0
        
        # Check if response contains credit card information
        if "card" in response.lower() or "credit" in response.lower():
            score += 0.3
        
        # Check for specific card types mentioned
        card_types = ["travel", "cashback", "business", "student", "rewards"]
        for card_type in card_types:
            if card_type in response.lower():
                score += 0.2
        
        # Check for financial details
        financial_terms = ["annual fee", "interest rate", "rewards", "bonus", "cashback"]
        for term in financial_terms:
            if term in response.lower():
                score += 0.1
        
        # Check for reasoning/explanation
        if "because" in response.lower() or "reason" in response.lower():
            score += 0.2
        
        return min(score, 1.0)


async def test_extractor_node():
    """Test the Extractor node using DeepEval metrics."""
    print("🧪 Testing Extractor Node...")
    
    test_cases = [
        LLMTestCase(
            input="I want a travel credit card for airline miles and international travel",
            expected_output="Should extract travel/miles goals with high confidence",
            context="User wants travel-focused credit card"
        ),
        LLMTestCase(
            input="I need a credit card with high cashback rewards for online shopping",
            expected_output="Should extract cashback goals with high confidence",
            context="User wants cashback-focused credit card"
        )
    ]
    
    llm_tool = MockLLMTool(use_openai=True)
    results = []
    
    for test_case in test_cases:
        try:
            # Extract information using the LLM tool
            schema = {
                "type": "object",
                "properties": {
                    "intent": {"type": "string"},
                    "goals": {"type": "array", "items": {"type": "string"}},
                    "jurisdiction": {"type": "string"},
                    "risk_tolerance": {"type": "string"}
                }
            }
            
            extracted = await llm_tool.nlu_extract(test_case.input, schema)
            response = str(extracted)
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_card_managers():
    """Test Card Manager nodes using DeepEval metrics."""
    print("\n🧪 Testing Card Manager Nodes...")
    
    test_cases = [
        LLMTestCase(
            input="Travel credit card with lounge access and travel insurance",
            expected_output="Should recommend travel cards with lounge access and insurance",
            context="User wants premium travel card with specific benefits"
        ),
        LLMTestCase(
            input="Cashback card for groceries and dining with no annual fee",
            expected_output="Should recommend cashback cards for groceries/dining with no annual fee",
            context="User wants no-fee cashback card for specific categories"
        )
    ]
    
    llm_tool = MockLLMTool(use_openai=True)
    policy_tool = MockPolicyTool()
    graph = create_credit_card_graph(llm_tool, policy_tool)
    
    results = []
    for test_case in test_cases:
        try:
            # Execute the graph
            initial_state = create_initial_state(test_case.input)
            result = await graph.ainvoke(initial_state)
            
            # Extract the final recommendations
            if 'final_recommendations' in result and result['final_recommendations']:
                final_recs = result['final_recommendations']
                response = f"Top recommendation: {final_recs.top_recommendation.card_name if final_recs.top_recommendation else 'None'}. Total cards: {final_recs.total_cards_analyzed}"
            else:
                response = "No final recommendations generated"
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_router_node():
    """Test the Router node using DeepEval metrics."""
    print("\n🧪 Testing Router Node...")
    
    test_cases = [
        LLMTestCase(
            input="I want to earn airline miles for international travel",
            expected_output="Should route to travel_manager",
            context="Travel-focused query should route to travel manager"
        ),
        LLMTestCase(
            input="Looking for high cashback on groceries and gas",
            expected_output="Should route to cashback_manager",
            context="Cashback-focused query should route to cashback manager"
        )
    ]
    
    llm_tool = MockLLMTool(use_openai=True)
    policy_tool = MockPolicyTool()
    graph = create_credit_card_graph(llm_tool, policy_tool)
    
    results = []
    for test_case in test_cases:
        try:
            # Execute the graph to see routing
            initial_state = create_initial_state(test_case.input)
            result = await graph.ainvoke(initial_state)
            
            # Check which manager was executed
            completed_nodes = result.get('completed_nodes', [])
            manager_nodes = ['travel_manager', 'cashback_manager', 'business_manager', 'student_manager', 'general_manager']
            
            executed_managers = [node for node in manager_nodes if node in completed_nodes]
            response = f"Executed managers: {', '.join(executed_managers)}"
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_summary_node():
    """Test the Summary node using DeepEval metrics."""
    print("\n🧪 Testing Summary Node...")
    
    test_cases = [
        LLMTestCase(
            input="I want a travel credit card with good rewards",
            expected_output="Should provide comprehensive summary with top travel card recommendations",
            context="Travel card request should generate detailed summary"
        ),
        LLMTestCase(
            input="Need cashback card for daily spending",
            expected_output="Should provide comprehensive summary with top cashback card recommendations",
            context="Cashback card request should generate detailed summary"
        )
    ]
    
    llm_tool = MockLLMTool(use_openai=True)
    policy_tool = MockPolicyTool()
    graph = create_credit_card_graph(llm_tool, policy_tool)
    
    results = []
    for test_case in test_cases:
        try:
            # Execute the graph
            initial_state = create_initial_state(test_case.input)
            result = await graph.ainvoke(initial_state)
            
            # Extract summary information
            if 'final_recommendations' in result and result['final_recommendations']:
                final_recs = result['final_recommendations']
                response = f"Summary: {len(final_recs.final_recommendations)} cards analyzed. Top card: {final_recs.top_recommendation.card_name if final_recs.top_recommendation else 'None'} with score {final_recs.top_recommendation.overall_score if final_recs.top_recommendation else 0:.2f}"
            else:
                response = "No summary generated"
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_overall_system():
    """Test the overall system performance using DeepEval metrics."""
    print("\n🧪 Testing Overall System...")
    
    test_cases = [
        LLMTestCase(
            input="I'm a frequent traveler and want a credit card that gives me airline miles, lounge access, and travel insurance. I travel internationally 4-5 times a year.",
            expected_output="Should provide comprehensive travel card recommendations with specific benefits mentioned",
            context="Complex travel card request with specific requirements"
        ),
        LLMTestCase(
            input="I'm a small business owner and need a credit card for business expenses. I want to track expenses, get employee cards, and earn rewards on business spending.",
            expected_output="Should provide comprehensive business card recommendations with business-specific features",
            context="Complex business card request with specific requirements"
        )
    ]
    
    llm_tool = MockLLMTool(use_openai=True)
    policy_tool = MockPolicyTool()
    graph = create_credit_card_graph(llm_tool, policy_tool)
    
    results = []
    for test_case in test_cases:
        try:
            # Execute the complete graph
            initial_state = create_initial_state(test_case.input)
            result = await graph.ainvoke(initial_state)
            
            # Extract comprehensive response
            if 'final_recommendations' in result and result['final_recommendations']:
                final_recs = result['final_recommendations']
                response = f"System processed request successfully. Generated {len(final_recs.final_recommendations)} recommendations. Top card: {final_recs.top_recommendation.card_name if final_recs.top_recommendation else 'None'} with score {final_recs.top_recommendation.overall_score if final_recs.top_recommendation else 0:.2f}. Total cards analyzed: {final_recs.total_cards_analyzed}"
            else:
                response = "System failed to generate recommendations"
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[AnswerRelevancyMetric(), AnswerCorrectnessMetric()]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def main():
    """Run all DeepEval tests."""
    print("🚀 DeepEval Testing Suite for Credit Card Recommendation System")
    print("=" * 70)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API key found: {api_key[:10]}...")
    else:
        print("⚠️ No OpenAI API key found - tests will use mock mode")
        print("💡 Set OPENAI_API_KEY environment variable to test real LLM")
    
    print()
    
    # Run all DeepEval tests
    test_functions = [
        test_extractor_node,
        test_card_managers,
        test_router_node,
        test_summary_node,
        test_overall_system
    ]
    
    all_results = []
    
    for test_func in test_functions:
        try:
            results = await test_func()
            all_results.extend(results)
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DeepEval Test Results Summary")
    print("=" * 70)
    
    if all_results:
        total_tests = len(all_results)
        avg_score = sum(result.score for result in all_results) / total_tests
        high_scores = sum(1 for result in all_results if result.score >= 0.8)
        medium_scores = sum(1 for result in all_results if 0.6 <= result.score < 0.8)
        low_scores = sum(1 for result in all_results if result.score < 0.6)
        
        print(f"✅ Total Tests: {total_tests}")
        print(f"📊 Average Score: {avg_score:.3f}")
        print(f"🎯 High Scores (≥0.8): {high_scores}")
        print(f"📈 Medium Scores (0.6-0.8): {medium_scores}")
        print(f"⚠️ Low Scores (<0.6): {low_scores}")
        
        # Detailed breakdown by metric
        print(f"\n📋 Detailed Results:")
        for i, result in enumerate(all_results[:5]):  # Show first 5 results
            print(f"   Test {i+1}: Score {result.score:.3f}")
        
        if avg_score >= 0.8:
            print(f"\n🎉 Excellent performance! System is highly reliable.")
        elif avg_score >= 0.6:
            print(f"\n✅ Good performance! System is reliable with room for improvement.")
        else:
            print(f"\n⚠️ Performance needs improvement. Review system logic.")
    
    else:
        print("❌ No test results available")
    
    return all_results


if __name__ == "__main__":
    asyncio.run(main())

