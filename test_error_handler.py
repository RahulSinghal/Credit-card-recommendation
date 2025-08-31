#!/usr/bin/env python3
"""
Test Error Handler Node
Validates the Error Handler Node in isolation.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.state import GraphState, RequestParsed, Consent
from src.nodes.error_handler import ErrorHandlerNode, ErrorHandlingResult
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


def test_error_handler_creation():
    """Test that the error handler can be created."""
    print("🧪 Testing Error Handler Creation...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        error_handler = ErrorHandlerNode(mock_llm, mock_policy)
        
        assert error_handler.node_type == "error_handler"
        print("   ✅ Error Handler created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error Handler creation failed: {str(e)}")
        return False


async def test_error_handler_execution():
    """Test full error handler execution with state."""
    print("\n🧪 Testing Error Handler Execution...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        error_handler = ErrorHandlerNode(mock_llm, mock_policy)
        
        # Create test state with some errors
        test_state = GraphState(
            session_id="test-session",
            user_query="I want a travel credit card for miles",
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
            errors=[
                {
                    "node": "extractor",
                    "error": "Failed to parse user query",
                    "timestamp": 1234567890.0,
                    "type": "error"
                }
            ],
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        # Execute the error handler
        result_state = await error_handler.execute(test_state)
        
        print(f"   ✅ Error handler executed successfully")
        print(f"   ✅ Current node: {result_state.current_node}")
        print(f"   ✅ Completed nodes: {result_state.completed_nodes}")
        
        # Check results
        if hasattr(result_state, 'error_handling'):
            error_handling = result_state.error_handling
            print(f"   ✅ Error handling results stored in state")
            print(f"   ✅ Total errors: {error_handling.get('total_errors', 0)}")
            print(f"   ✅ Handling time: {error_handling.get('handling_time', 0):.3f}s")
            
            if 'result' in error_handling:
                result = error_handling['result']
                print(f"   ✅ Errors handled: {result.errors_handled}")
                print(f"   ✅ Can continue: {result.can_continue}")
                print(f"   ✅ User message: {result.user_friendly_message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handler execution test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_node_creation():
    """Test that the error handler node can be created."""
    print("\n🧪 Testing Error Handler Node Creation...")
    
    try:
        from src.nodes.error_handler import create_error_handler_node
        
        error_handler_node = create_error_handler_node()
        
        # Test that it's callable
        assert callable(error_handler_node)
        print("   ✅ Error handler node created successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handler node creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all error handler tests."""
    print("🚀 ERROR HANDLER NODE TESTING")
    print("=" * 60)
    
    # Test 1: Handler creation
    creation_success = test_error_handler_creation()
    
    # Test 2: Full execution
    execution_success = await test_error_handler_execution()
    
    # Test 3: Node creation
    node_success = await test_node_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ERROR HANDLER TEST RESULTS")
    print("=" * 60)
    print(f"Handler Creation: {'✅ PASSED' if creation_success else '❌ FAILED'}")
    print(f"Full Execution: {'✅ PASSED' if execution_success else '❌ FAILED'}")
    print(f"Node Creation: {'✅ PASSED' if node_success else '❌ FAILED'}")
    
    overall_success = all([
        creation_success, execution_success, node_success
    ])
    
    if overall_success:
        print("\n🎉 All Error Handler tests passed!")
        print("✅ The Error Handler Node is working correctly.")
        print("✅ Ready for graph integration.")
        return 0
    else:
        print("\n💥 Some Error Handler tests failed.")
        print("❌ Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
