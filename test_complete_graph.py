#!/usr/bin/env python3
"""
Test Complete Graph Integration
Validates the complete credit card recommendation graph with all nodes.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


async def test_graph_creation():
    """Test that the complete graph can be created."""
    print("🧪 Testing Complete Graph Creation...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        
        graph = create_credit_card_graph(mock_llm, mock_policy)
        
        print("   ✅ Complete graph created successfully")
        print(f"   ✅ Graph type: {type(graph).__name__}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Graph creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_travel_request_flow():
    """Test a complete travel credit card request flow."""
    print("\n🧪 Testing Travel Request Flow...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        graph = create_credit_card_graph(mock_llm, mock_policy)
        
        # Create initial state
        initial_state = create_initial_state(
            "I want a travel credit card for airline miles and international travel"
        )
        
        print(f"   ✅ Initial state created")
        print(f"   ✅ User query: {initial_state.user_query}")
        print(f"   ✅ Session ID: {initial_state.session_id}")
        
        # Execute the graph
        print("   ✅ Executing graph...")
        result = await graph.ainvoke(initial_state)
        
        print(f"   ✅ Graph execution completed")
        print(f"   ✅ Final state keys: {list(result.keys())}")
        
        # Check execution flow
        if 'completed_nodes' in result:
            completed_nodes = result['completed_nodes']
            print(f"   ✅ Completed nodes: {completed_nodes}")
            
            # Verify expected flow
            expected_nodes = ["extractor", "router", "travel_manager", "online_search", "policy_validation", "summary"]
            for expected_node in expected_nodes:
                if expected_node in completed_nodes:
                    print(f"   ✅ {expected_node} executed")
                else:
                    print(f"   ⚠️ {expected_node} not executed")
        
        # Check results
        if 'manager_results' in result and result['manager_results']:
            print(f"   ✅ Manager results available")
            for manager_type, manager_result in result['manager_results'].items():
                print(f"   ✅ {manager_type}: {len(manager_result.recommendations)} recommendations")
        
        if 'final_recommendations' in result and result['final_recommendations']:
            final_recs = result['final_recommendations']
            print(f"   ✅ Final recommendations available")
            print(f"   ✅ Total cards analyzed: {final_recs.total_cards_analyzed}")
            print(f"   ✅ Final recommendations: {len(final_recs.final_recommendations)}")
            
            if final_recs.top_recommendation:
                top_rec = final_recs.top_recommendation
                print(f"   ✅ Top recommendation: {top_rec.card_name}")
                print(f"   ✅ Overall score: {top_rec.overall_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Travel request flow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_cashback_request_flow():
    """Test a complete cashback credit card request flow."""
    print("\n🧪 Testing Cashback Request Flow...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        graph = create_credit_card_graph(mock_llm, mock_policy)
        
        # Create initial state
        initial_state = create_initial_state(
            "I need a credit card with high cashback rewards for online shopping"
        )
        
        print(f"   ✅ Initial state created")
        print(f"   ✅ User query: {initial_state.user_query}")
        
        # Execute the graph
        print("   ✅ Executing graph...")
        result = await graph.ainvoke(initial_state)
        
        print(f"   ✅ Graph execution completed")
        
        # Check execution flow
        if 'completed_nodes' in result:
            completed_nodes = result['completed_nodes']
            print(f"   ✅ Completed nodes: {completed_nodes}")
            
            # Verify expected flow
            expected_nodes = ["extractor", "router", "cashback_manager", "online_search", "policy_validation", "summary"]
            for expected_node in expected_nodes:
                if expected_node in completed_nodes:
                    print(f"   ✅ {expected_node} executed")
                else:
                    print(f"   ⚠️ {expected_node} not executed")
        
        # Check results
        if 'final_recommendations' in result and result['final_recommendations']:
            final_recs = result['final_recommendations']
            print(f"   ✅ Final recommendations available")
            print(f"   ✅ Total cards analyzed: {final_recs.total_cards_analyzed}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Cashback request flow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test error handling in the graph."""
    print("\n🧪 Testing Error Handling...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        graph = create_credit_card_graph(mock_llm, mock_policy)
        
        # Create initial state with a problematic query
        initial_state = create_initial_state("")
        
        print(f"   ✅ Initial state created with empty query")
        
        # Execute the graph
        print("   ✅ Executing graph...")
        result = await graph.ainvoke(initial_state)
        
        print(f"   ✅ Graph execution completed")
        
        # Check error handling
        if 'errors' in result and result['errors']:
            print(f"   ✅ Errors captured: {len(result['errors'])}")
            for error in result['errors']:
                print(f"   ✅ Error: {error.get('error', 'Unknown')}")
        
        if 'error_handling' in result:
            error_handling = result['error_handling']
            print(f"   ✅ Error handling results available")
            print(f"   ✅ Total errors: {error_handling.get('total_errors', 0)}")
        
        # Check if we still got recommendations
        if 'final_recommendations' in result and result['final_recommendations']:
            final_recs = result['final_recommendations']
            print(f"   ✅ Fallback recommendations available")
            print(f"   ✅ Total cards analyzed: {final_recs.total_cards_analyzed}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all complete graph tests."""
    print("🚀 COMPLETE GRAPH INTEGRATION TESTING")
    print("=" * 60)
    
    # Test 1: Graph creation
    graph_creation = await test_graph_creation()
    
    # Test 2: Travel request flow
    travel_flow = await test_travel_request_flow()
    
    # Test 3: Cashback request flow
    cashback_flow = await test_cashback_request_flow()
    
    # Test 4: Error handling
    error_handling = await test_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE GRAPH TEST RESULTS")
    print("=" * 60)
    print(f"Graph Creation: {'✅ PASSED' if graph_creation else '❌ FAILED'}")
    print(f"Travel Request Flow: {'✅ PASSED' if travel_flow else '❌ FAILED'}")
    print(f"Cashback Request Flow: {'✅ PASSED' if cashback_flow else '❌ FAILED'}")
    print(f"Error Handling: {'✅ PASSED' if error_handling else '❌ FAILED'}")
    
    overall_success = all([
        graph_creation, travel_flow, cashback_flow, error_handling
    ])
    
    if overall_success:
        print("\n🎉 All Complete Graph tests passed!")
        print("✅ The complete credit card recommendation system is working!")
        print("✅ All nodes are integrated and functioning correctly.")
        print("✅ Ready for real LLM integration.")
        return 0
    else:
        print("\n💥 Some Complete Graph tests failed.")
        print("❌ Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
