#!/usr/bin/env python3
"""
Test Router Agent in Isolation
Validates the Router Agent's goal-based routing logic.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.state import GraphState, RequestParsed, Consent
from src.graph.credit_card_graph import _determine_manager_categories


def test_router_routing_logic():
    """Test the router's goal-based routing logic."""
    print("🧪 Testing Router Agent Routing Logic...")
    
    # Test cases with different goals
    test_cases = [
        {
            "name": "Travel-focused request",
            "goals": ["miles", "travel"],
            "expected": ["travel_manager"]
        },
        {
            "name": "Cashback-focused request", 
            "goals": ["cashback"],
            "expected": ["cashback_manager"]
        },
        {
            "name": "Business-focused request",
            "goals": ["business_expenses", "business"],
            "expected": ["business_manager"]
        },
        {
            "name": "Student-focused request",
            "name": "Student-focused request",
            "goals": ["student", "building_credit"],
            "expected": ["student_manager"]
        },
        {
            "name": "Mixed goals request",
            "goals": ["miles", "cashback"],
            "expected": ["travel_manager", "cashback_manager"]
        },
        {
            "name": "Generic rewards request",
            "goals": ["rewards"],
            "expected": ["general_manager"]
        },
        {
            "name": "Empty goals request",
            "goals": [],
            "expected": ["general_manager"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Goals: {test_case['goals']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Create a mock request object
        mock_request = type('MockRequest', (), {
            'goals': test_case['goals']
        })()
        
        # Test the routing logic
        try:
            result = _determine_manager_categories(mock_request)
            print(f"   Result: {result}")
            
            # Validate the result
            if set(result) == set(test_case['expected']):
                print("   ✅ PASSED")
            else:
                print(f"   ❌ FAILED - Expected {test_case['expected']}, got {result}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            all_passed = False
    
    return all_passed


async def test_router_node_execution():
    """Test the actual router node execution."""
    print("\n🧪 Testing Router Node Execution...")
    
    try:
        from src.graph.credit_card_graph import _create_router_node
        
        # Create the router node
        router_node = _create_router_node()
        
        # Create test state with parsed request
        test_state = GraphState(
            session_id="test-session",
            user_query="I want a travel credit card",
            locale="en-SG",
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            request=RequestParsed(
                intent="recommend_card",
                goals=["miles", "travel"],
                constraints={},
                jurisdiction="SG",
                risk_tolerance="standard",
                time_horizon="12m"
            ),
            policy_pack={},
            catalog_meta={},
            fanout_plan=None,
            manager_results={},
            final_recommendations=None,
            telemetry={"events": []},
            errors=[],
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        print("✅ Test state created successfully")
        print(f"   Initial fanout_plan: {test_state.fanout_plan}")
        print(f"   Initial completed_nodes: {test_state.completed_nodes}")
        
        # Execute the router node
        print("✅ Executing router node...")
        result_state = await router_node(test_state)
        
        print("✅ Router node executed successfully")
        print(f"   Final fanout_plan: {result_state.fanout_plan}")
        print(f"   Completed nodes: {result_state.completed_nodes}")
        print(f"   Current node: {result_state.current_node}")
        print(f"   Next nodes: {result_state.next_nodes}")
        
        # Validate the results
        if result_state.fanout_plan == ["travel_manager"]:
            print("   ✅ Routing logic working correctly")
            return True
        else:
            print(f"   ❌ Unexpected fanout_plan: {result_state.fanout_plan}")
            return False
            
    except Exception as e:
        print(f"❌ Router node test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_router_error_handling():
    """Test router error handling scenarios."""
    print("\n🧪 Testing Router Error Handling...")
    
    try:
        from src.graph.credit_card_graph import _create_router_node
        
        # Create the router node
        router_node = _create_router_node()
        
        # Test case 1: No request in state
        print("   Testing: No request in state")
        test_state = GraphState(
            session_id="test-session",
            user_query="I want a travel credit card",
            locale="en-SG",
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            request=None,  # No request - should cause error
            policy_pack={},
            catalog_meta={},
            fanout_plan=None,
            manager_results={},
            final_recommendations=None,
            telemetry={"events": []},
            errors=[],
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        try:
            result_state = await router_node(test_state)
            print("   ❌ Should have raised an error for missing request")
            return False
        except ValueError as e:
            if "No parsed request available for routing" in str(e):
                print("   ✅ Correctly handled missing request error")
            else:
                print(f"   ❌ Unexpected error message: {str(e)}")
                return False
        
        # Test case 2: State with errors
        print("   Testing: State with existing errors")
        test_state = GraphState(
            session_id="test-session",
            user_query="I want a travel credit card",
            locale="en-SG",
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            request=RequestParsed(
                intent="recommend_card",
                goals=["miles", "travel"],
                constraints={},
                jurisdiction="SG",
                risk_tolerance="standard",
                time_horizon="12m"
            ),
            policy_pack={},
            catalog_meta={},
            fanout_plan=None,
            manager_results={},
            final_recommendations=None,
            telemetry={"events": []},
            errors=[{"node": "extractor", "error": "Test error"}],  # Existing error
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        result_state = await router_node(test_state)
        print(f"   ✅ Router handled existing errors gracefully")
        print(f"   Error count: {len(result_state.errors)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Router error handling test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all router agent tests."""
    print("🚀 ROUTER AGENT TESTING")
    print("=" * 60)
    
    # Test 1: Routing logic
    routing_success = test_router_routing_logic()
    
    # Test 2: Node execution
    execution_success = await test_router_node_execution()
    
    # Test 3: Error handling
    error_handling_success = await test_router_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ROUTER AGENT TEST RESULTS")
    print("=" * 60)
    print(f"Routing Logic: {'✅ PASSED' if routing_success else '❌ FAILED'}")
    print(f"Node Execution: {'✅ PASSED' if execution_success else '❌ FAILED'}")
    print(f"Error Handling: {'✅ PASSED' if error_handling_success else '❌ FAILED'}")
    
    overall_success = routing_success and execution_success and error_handling_success
    
    if overall_success:
        print("\n🎉 All Router Agent tests passed!")
        print("✅ The Router Agent is working correctly.")
        print("✅ Goal-based routing logic is functioning.")
        print("✅ Error handling is robust.")
        return 0
    else:
        print("\n💥 Some Router Agent tests failed.")
        print("❌ Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
