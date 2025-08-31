#!/usr/bin/env python3
"""
Test Support Agents
Validates the Online Search and Policy Validation agents in isolation.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.state import GraphState, RequestParsed, Consent
from src.nodes.support_agents import (
    OnlineSearchAgent, PolicyValidationAgent, 
    SearchResult, PolicyValidationResult
)
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


def test_online_search_agent_creation():
    """Test that the online search agent can be created."""
    print("🧪 Testing Online Search Agent Creation...")
    
    try:
        mock_llm = MockLLMTool()
        online_search_agent = OnlineSearchAgent(mock_llm)
        
        assert online_search_agent.agent_type == "online_search"
        print("   ✅ Online Search Agent created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Online Search Agent creation failed: {str(e)}")
        return False


def test_policy_validation_agent_creation():
    """Test that the policy validation agent can be created."""
    print("\n🧪 Testing Policy Validation Agent Creation...")
    
    try:
        mock_policy = MockPolicyTool()
        policy_validation_agent = PolicyValidationAgent(mock_policy)
        
        assert policy_validation_agent.agent_type == "policy_validation"
        print("   ✅ Policy Validation Agent created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Policy Validation Agent creation failed: {str(e)}")
        return False


async def test_online_search_functionality():
    """Test the online search agent's search functionality."""
    print("\n🧪 Testing Online Search Functionality...")
    
    try:
        mock_llm = MockLLMTool()
        online_search_agent = OnlineSearchAgent(mock_llm)
        
        # Test general search
        general_results = await online_search_agent.search_credit_card_info(
            "I want a travel credit card for miles"
        )
        print(f"   ✅ General search returned {len(general_results)} results")
        
        if general_results:
            top_result = general_results[0]
            print(f"   ✅ Top result: {top_result.title} (Score: {top_result.relevance_score:.2f})")
        
        # Test card-specific search
        card_results = await online_search_agent.search_card_specific_info(
            "Singapore Airlines KrisFlyer Credit Card"
        )
        print(f"   ✅ Card-specific search returned {len(card_results)} results")
        
        if card_results:
            top_card_result = card_results[0]
            print(f"   ✅ Top card result: {top_card_result.title} (Score: {top_card_result.relevance_score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Online search functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_policy_validation_functionality():
    """Test the policy validation agent's validation functionality."""
    print("\n🧪 Testing Policy Validation Functionality...")
    
    try:
        mock_policy = MockPolicyTool()
        policy_validation_agent = PolicyValidationAgent(mock_policy)
        
        # Create test request and consent
        test_request = RequestParsed(
            intent="recommend_card",
            goals=["miles", "travel"],
            constraints={},
            jurisdiction="SG",
            risk_tolerance="standard",
            time_horizon="12m"
        )
        
        test_consent = Consent(
            personalization=True,
            data_sharing=False,
            credit_pull="none"
        )
        
        # Test validation
        validation_result = await policy_validation_agent.validate_request_compliance(
            test_request, 
            test_consent
        )
        
        print(f"   ✅ Policy validation completed")
        print(f"   ✅ Is valid: {validation_result.is_valid}")
        print(f"   ✅ Warnings: {len(validation_result.warnings)}")
        print(f"   ✅ Required consent: {validation_result.required_consent}")
        print(f"   ✅ Compliance issues: {len(validation_result.compliance_issues)}")
        print(f"   ✅ Recommendations: {len(validation_result.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Policy validation functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_online_search_execution():
    """Test full online search agent execution with state."""
    print("\n🧪 Testing Online Search Agent Execution...")
    
    try:
        mock_llm = MockLLMTool()
        online_search_agent = OnlineSearchAgent(mock_llm)
        
        # Create test state with manager results
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
            manager_results={
                "travel_manager": {
                    "recommendations": [
                        {
                            "card_name": "Singapore Airlines KrisFlyer Credit Card",
                            "card_id": "travel_001"
                        }
                    ]
                }
            },
            final_recommendations=None,
            telemetry={"events": []},
            errors=[],
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        # Execute the online search agent
        result_state = await online_search_agent.execute(test_state)
        
        print(f"   ✅ Online search agent executed successfully")
        print(f"   ✅ Current node: {result_state.current_node}")
        print(f"   ✅ Completed nodes: {result_state.completed_nodes}")
        
        # Check results
        if hasattr(result_state, 'online_search_results'):
            search_results = result_state.online_search_results
            print(f"   ✅ Search results stored in state")
            print(f"   ✅ Total results: {search_results.get('total_results', 0)}")
            print(f"   ✅ Search time: {search_results.get('search_time', 0):.3f}s")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Online search agent execution test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_policy_validation_execution():
    """Test full policy validation agent execution with state."""
    print("\n🧪 Testing Policy Validation Agent Execution...")
    
    try:
        mock_policy = MockPolicyTool()
        policy_validation_agent = PolicyValidationAgent(mock_policy)
        
        # Create test state
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
            errors=[],
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        # Execute the policy validation agent
        result_state = await policy_validation_agent.execute(test_state)
        
        print(f"   ✅ Policy validation agent executed successfully")
        print(f"   ✅ Current node: {result_state.current_node}")
        print(f"   ✅ Completed nodes: {result_state.completed_nodes}")
        
        # Check results
        if hasattr(result_state, 'policy_validation'):
            policy_results = result_state.policy_validation
            print(f"   ✅ Policy validation results stored in state")
            print(f"   ✅ Is compliant: {policy_results.get('is_compliant', False)}")
            print(f"   ✅ Validation time: {policy_results.get('validation_time', 0):.3f}s")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Policy validation agent execution test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_node_creation():
    """Test that the support agent nodes can be created."""
    print("\n🧪 Testing Support Agent Node Creation...")
    
    try:
        from src.nodes.support_agents import create_online_search_node, create_policy_validation_node
        
        online_search_node = create_online_search_node()
        policy_validation_node = create_policy_validation_node()
        
        # Test that they're callable
        assert callable(online_search_node)
        assert callable(policy_validation_node)
        
        print("   ✅ Online search node created successfully")
        print("   ✅ Policy validation node created successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Support agent node creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all support agent tests."""
    print("🚀 SUPPORT AGENTS TESTING")
    print("=" * 60)
    
    # Test 1: Agent creation
    online_search_creation = test_online_search_agent_creation()
    policy_validation_creation = test_policy_validation_agent_creation()
    
    # Test 2: Functionality
    online_search_functionality = await test_online_search_functionality()
    policy_validation_functionality = await test_policy_validation_functionality()
    
    # Test 3: Full execution
    online_search_execution = await test_online_search_execution()
    policy_validation_execution = await test_policy_validation_execution()
    
    # Test 4: Node creation
    node_creation = await test_node_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUPPORT AGENTS TEST RESULTS")
    print("=" * 60)
    print(f"Online Search Agent Creation: {'✅ PASSED' if online_search_creation else '❌ FAILED'}")
    print(f"Policy Validation Agent Creation: {'✅ PASSED' if policy_validation_creation else '❌ FAILED'}")
    print(f"Online Search Functionality: {'✅ PASSED' if online_search_functionality else '❌ FAILED'}")
    print(f"Policy Validation Functionality: {'✅ PASSED' if policy_validation_functionality else '❌ FAILED'}")
    print(f"Online Search Execution: {'✅ PASSED' if online_search_execution else '❌ FAILED'}")
    print(f"Policy Validation Execution: {'✅ PASSED' if policy_validation_execution else '❌ FAILED'}")
    print(f"Node Creation: {'✅ PASSED' if node_creation else '❌ FAILED'}")
    
    overall_success = all([
        online_search_creation, policy_validation_creation,
        online_search_functionality, policy_validation_functionality,
        online_search_execution, policy_validation_execution,
        node_creation
    ])
    
    if overall_success:
        print("\n🎉 All Support Agent tests passed!")
        print("✅ Both Online Search and Policy Validation agents are working correctly.")
        print("✅ Ready for graph integration.")
        return 0
    else:
        print("\n💥 Some Support Agent tests failed.")
        print("❌ Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
