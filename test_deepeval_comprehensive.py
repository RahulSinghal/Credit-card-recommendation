#!/usr/bin/env python3
"""
DeepEval Comprehensive Testing Suite
Advanced evaluation of the credit card recommendation system using DeepEval.
Tests each node individually and the overall system performance.
"""

import asyncio
import sys
import os
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric, 
    ContextRelevancyMetric, 
    ContextRecallMetric, 
    FaithfulnessMetric,
    AnswerCorrectnessMetric,
    CustomMetric
)
from deepeval.test_case import LLMTestCase
from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


class CreditCardRelevancyMetric(CustomMetric):
    """Custom metric for credit card recommendation relevancy."""
    
    def __init__(self):
        super().__init__()
    
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


class CreditCardAccuracyMetric(CustomMetric):
    """Custom metric for credit card recommendation accuracy."""
    
    def __init__(self):
        super().__init__()
    
    def measure(self, test_case: LLMTestCase, response: str) -> float:
        """Measure accuracy of credit card recommendations."""
        score = 0.0
        
        # Check if response matches the expected card type
        query = test_case.input.lower()
        response_lower = response.lower()
        
        # Travel card queries
        if any(word in query for word in ["travel", "miles", "airline"]):
            if any(word in response_lower for word in ["travel", "miles", "airline", "krisflyer"]):
                score += 0.4
        
        # Cashback card queries
        if any(word in query for word in ["cashback", "cash", "money"]):
            if any(word in response_lower for word in ["cashback", "cash", "rewards"]):
                score += 0.4
        
        # Business card queries
        if any(word in query for word in ["business", "corporate", "expense"]):
            if any(word in response_lower for word in ["business", "corporate", "expense"]):
                score += 0.4
        
        # Student card queries
        if any(word in query for word in ["student", "college", "university"]):
            if any(word in response_lower for word in ["student", "college", "university"]):
                score += 0.4
        
        # Check for specific card names
        specific_cards = [
            "singapore airlines", "krisflyer", "dbs live fresh", "ocbc 365",
            "uob business", "posb everyday"
        ]
        for card in specific_cards:
            if card in response_lower:
                score += 0.3
        
        # Check for numerical information
        import re
        numbers = re.findall(r'\d+\.?\d*', response)
        if len(numbers) >= 2:  # At least annual fee and rewards rate
            score += 0.2
        
        return min(score, 1.0)


async def test_extractor_node_deepeval():
    """Test the Extractor node using DeepEval metrics."""
    print("🧪 Testing Extractor Node with DeepEval...")
    
    # Create test cases
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
        ),
        LLMTestCase(
            input="Looking for a business credit card for corporate expenses",
            expected_output="Should extract business goals with high confidence",
            context="User wants business-focused credit card"
        ),
        LLMTestCase(
            input="I'm a student and need my first credit card",
            expected_output="Should extract student/building_credit goals",
            context="User is a student seeking first credit card"
        )
    ]
    
    # Create LLM tool
    llm_tool = MockLLMTool(use_openai=True)
    
    # Test each case
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
                metrics=[
                    AnswerRelevancyMetric(),
                    AnswerCorrectnessMetric(),
                    CreditCardRelevancyMetric(),
                    CreditCardAccuracyMetric()
                ]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_card_managers_deepeval():
    """Test Card Manager nodes using DeepEval metrics."""
    print("\n🧪 Testing Card Manager Nodes with DeepEval...")
    
    # Create test cases for different card types
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
        ),
        LLMTestCase(
            input="Business card for expense tracking and employee cards",
            expected_output="Should recommend business cards with expense tracking and employee features",
            context="User wants business card with specific corporate features"
        )
    ]
    
    # Create tools and graph
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
                metrics=[
                    AnswerRelevancyMetric(),
                    AnswerCorrectnessMetric(),
                    CreditCardRelevancyMetric(),
                    CreditCardAccuracyMetric()
                ]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_router_node_deepeval():
    """Test the Router node using DeepEval metrics."""
    print("\n🧪 Testing Router Node with DeepEval...")
    
    # Create test cases for routing logic
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
        ),
        LLMTestCase(
            input="Need a corporate card for business expenses",
            expected_output="Should route to business_manager",
            context="Business-focused query should route to business manager"
        ),
        LLMTestCase(
            input="Student seeking first credit card to build credit",
            expected_output="Should route to student_manager",
            context="Student-focused query should route to student manager"
        )
    ]
    
    # Create tools and graph
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
                metrics=[
                    AnswerRelevancyMetric(),
                    AnswerCorrectnessMetric()
                ]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_summary_node_deepeval():
    """Test the Summary node using DeepEval metrics."""
    print("\n🧪 Testing Summary Node with DeepEval...")
    
    # Create test cases for summary generation
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
    
    # Create tools and graph
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
                metrics=[
                    AnswerRelevancyMetric(),
                    AnswerCorrectnessMetric(),
                    CreditCardRelevancyMetric(),
                    CreditCardAccuracyMetric()
                ]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_overall_system_deepeval():
    """Test the overall system performance using DeepEval metrics."""
    print("\n🧪 Testing Overall System with DeepEval...")
    
    # Create comprehensive test cases
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
        ),
        LLMTestCase(
            input="I'm a college student with no credit history. I want my first credit card to build credit and get some rewards. I prefer no annual fee.",
            expected_output="Should provide student-friendly credit card recommendations with no annual fee",
            context="Student credit card request with specific constraints"
        )
    ]
    
    # Create tools and graph
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
                metrics=[
                    AnswerRelevancyMetric(),
                    AnswerCorrectnessMetric(),
                    CreditCardRelevancyMetric(),
                    CreditCardAccuracyMetric()
                ]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50]}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def test_error_handling_deepeval():
    """Test error handling scenarios using DeepEval metrics."""
    print("\n🧪 Testing Error Handling with DeepEval...")
    
    # Create test cases for error scenarios
    test_cases = [
        LLMTestCase(
            input="",  # Empty query
            expected_output="Should handle gracefully and provide helpful error message",
            context="Empty query should trigger error handling"
        ),
        LLMTestCase(
            input="This is a completely unrelated query about cooking recipes",
            expected_output="Should handle gracefully and provide relevant response or error message",
            context="Unrelated query should be handled appropriately"
        )
    ]
    
    # Create tools and graph
    llm_tool = MockLLMTool(use_openai=True)
    policy_tool = MockPolicyTool()
    graph = create_credit_card_graph(llm_tool, policy_tool)
    
    results = []
    for test_case in test_cases:
        try:
            # Execute the graph
            initial_state = create_initial_state(test_case.input)
            result = await graph.ainvoke(initial_state)
            
            # Check for errors in the result
            errors = result.get('errors', [])
            if errors:
                response = f"System handled error gracefully. Errors: {errors}"
            else:
                response = "System processed request without errors"
            
            # Evaluate using DeepEval
            test_result = evaluate(
                test_case,
                response,
                metrics=[
                    AnswerRelevancyMetric(),
                    AnswerCorrectnessMetric()
                ]
            )
            
            results.append(test_result)
            print(f"   ✅ {test_case.input[:50] if test_case.input else 'Empty query'}... - Score: {test_result.score:.2f}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    return results


async def main():
    """Run all DeepEval tests."""
    print("🚀 DeepEval Comprehensive Testing Suite")
    print("=" * 60)
    
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
        test_extractor_node_deepeval,
        test_card_managers_deepeval,
        test_router_node_deepeval,
        test_summary_node_deepeval,
        test_overall_system_deepeval,
        test_error_handling_deepeval
    ]
    
    all_results = []
    
    for test_func in test_functions:
        try:
            results = await test_func()
            all_results.extend(results)
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DeepEval Test Results Summary")
    print("=" * 60)
    
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

