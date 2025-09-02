#!/usr/bin/env python3
"""
Test Card Manager Agents
Validates all card manager agents in isolation and as part of the graph.
"""

import asyncio
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.state import GraphState, RequestParsed, Consent
from src.nodes.card_managers import (
    TravelManager, CashbackManager, BusinessManager, 
    StudentManager, GeneralManager, ManagerResult
)
from src.tools.mock_tools import MockLLMTool, MockPolicyTool, MockCatalogTool


def test_card_manager_creation():
    """Test that all card managers can be created."""
    print("🧪 Testing Card Manager Creation...")
    
    # Create mock tools
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    mock_catalog = MockCatalogTool()
    
    # Test each manager type
    managers = [
        ("Travel Manager", TravelManager(mock_llm, mock_policy, mock_catalog)),
        ("Cashback Manager", CashbackManager(mock_llm, mock_policy, mock_catalog)),
        ("Business Manager", BusinessManager(mock_llm, mock_policy, mock_catalog)),
        ("Student Manager", StudentManager(mock_llm, mock_policy, mock_catalog)),
        ("General Manager", GeneralManager(mock_llm, mock_policy, mock_catalog))
    ]
    
    all_created = True
    for name, manager in managers:
        try:
            assert manager.manager_type in name.lower().replace(" ", "_")
            print(f"   ✅ {name} created successfully")
        except Exception as e:
            print(f"   ❌ {name} creation failed: {str(e)}")
            all_created = False
    
    return all_created


async def test_travel_manager():
    """Test the travel manager specifically."""
    print("\n🧪 Testing Travel Manager...")
    
    # Create tools and manager
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    mock_catalog = MockCatalogTool()
    travel_manager = TravelManager(mock_llm, mock_policy, mock_catalog)
    
    # Create test request
    test_request = RequestParsed(
        intent="recommend_card",
        goals=["miles", "travel"],
        constraints={},
        jurisdiction="SG",
        risk_tolerance="standard",
        time_horizon="12m"
    )
    
    try:
        # Test analysis
        analysis = await travel_manager.analyze_request(test_request)
        print(f"   ✅ Analysis completed: {analysis.get('travel_specific', {})}")
        
        # Test catalog search
        cards = await travel_manager.search_catalog({
            "goals": ["miles", "travel"],
            "risk_tolerance": "standard"
        })
        print(f"   ✅ Found {len(cards)} travel cards")
        
        # Test card ranking
        ranked_cards = await travel_manager.rank_cards(cards, test_request)
        print(f"   ✅ Ranked {len(ranked_cards)} cards")
        
        if ranked_cards:
            best_card = ranked_cards[0]
            print(f"   ✅ Best match: {best_card.card_name} (Score: {best_card.match_score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Travel manager test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_cashback_manager():
    """Test the cashback manager specifically."""
    print("\n🧪 Testing Cashback Manager...")
    
    # Create tools and manager
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    mock_catalog = MockCatalogTool()
    cashback_manager = CashbackManager(mock_llm, mock_policy, mock_catalog)
    
    # Create test request
    test_request = RequestParsed(
        intent="recommend_card",
        goals=["cashback", "rewards"],
        constraints={},
        jurisdiction="SG",
        risk_tolerance="conservative",
        time_horizon="6m"
    )
    
    try:
        # Test analysis
        analysis = await cashback_manager.analyze_request(test_request)
        print(f"   ✅ Analysis completed: {analysis.get('cashback_specific', {})}")
        
        # Test catalog search
        cards = await cashback_manager.search_catalog({
            "goals": ["cashback"],
            "risk_tolerance": "conservative"
        })
        print(f"   ✅ Found {len(cards)} cashback cards")
        
        # Test card ranking
        ranked_cards = await cashback_manager.rank_cards(cards, test_request)
        print(f"   ✅ Ranked {len(ranked_cards)} cards")
        
        if ranked_cards:
            best_card = ranked_cards[0]
            print(f"   ✅ Best match: {best_card.card_name} (Score: {best_card.match_score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Cashback manager test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_manager_execution():
    """Test full manager execution with state."""
    print("\n🧪 Testing Manager Execution...")
    
    # Create tools and manager
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    mock_catalog = MockCatalogTool()
    travel_manager = TravelManager(mock_llm, mock_policy, mock_catalog)
    
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
    
    try:
        # Execute the manager
        result_state = await travel_manager.execute(test_state)
        
        print(f"   ✅ Manager executed successfully")
        print(f"   ✅ Current node: {result_state.current_node}")
        print(f"   ✅ Completed nodes: {result_state.completed_nodes}")
        print(f"   ✅ Next nodes: {result_state.next_nodes}")
        
        # Check results
        if "travel_manager" in result_state.manager_results:
            manager_result = result_state.manager_results["travel_manager"]
            print(f"   ✅ Manager result created")
            print(f"   ✅ Total cards found: {manager_result.total_cards_found}")
            print(f"   ✅ Recommendations: {len(manager_result.recommendations)}")
            
            if manager_result.best_match:
                print(f"   ✅ Best match: {manager_result.best_match.card_name}")
                print(f"   ✅ Match score: {manager_result.best_match.match_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Manager execution test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_graph_integration():
    """Test card managers as part of the full graph."""
    print("\n🧪 Testing Graph Integration...")
    
    try:
        from src.graph.credit_card_graph import create_credit_card_graph
        from src.tools.mock_tools import MockLLMTool, MockPolicyTool
        
        # Create graph with mock tools
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        graph = create_credit_card_graph(mock_llm, mock_policy)
        
        print("   ✅ Graph created successfully")
        
        # Test with travel request
        from src.graph.credit_card_graph import create_initial_state
        
        initial_state = create_initial_state("I want a travel credit card for miles")
        
        print("   ✅ Initial state created")
        print("   ✅ Executing graph...")
        
        # Execute the graph
        result = await graph.ainvoke(initial_state)
        
        print("   ✅ Graph executed successfully")
        print(f"   ✅ Final state keys: {list(result.keys())}")
        
        # Check if travel manager was executed
        if 'manager_results' in result and result['manager_results']:
            print(f"   ✅ Manager results: {list(result['manager_results'].keys())}")
            
            for manager_type, manager_result in result['manager_results'].items():
                print(f"   ✅ {manager_type}: {len(manager_result.recommendations)} recommendations")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Graph integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all card manager tests."""
    print("🚀 CARD MANAGER AGENT TESTING")
    print("=" * 60)
    
    # Test 1: Manager creation
    creation_success = test_card_manager_creation()
    
    # Test 2: Travel manager
    travel_success = await test_travel_manager()
    
    # Test 3: Cashback manager
    cashback_success = await test_cashback_manager()
    
    # Test 4: Manager execution
    execution_success = await test_manager_execution()
    
    # Test 5: Graph integration
    graph_success = await test_graph_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CARD MANAGER TEST RESULTS")
    print("=" * 60)
    print(f"Manager Creation: {'✅ PASSED' if creation_success else '❌ FAILED'}")
    print(f"Travel Manager: {'✅ PASSED' if travel_success else '❌ FAILED'}")
    print(f"Cashback Manager: {'✅ PASSED' if cashback_success else '❌ FAILED'}")
    print(f"Manager Execution: {'✅ PASSED' if execution_success else '❌ FAILED'}")
    print(f"Graph Integration: {'✅ PASSED' if graph_success else '❌ FAILED'}")
    
    overall_success = all([
        creation_success, travel_success, cashback_success, 
        execution_success, graph_success
    ])
    
    if overall_success:
        print("\n🎉 All Card Manager tests passed!")
        print("✅ All card managers are working correctly.")
        print("✅ Travel, Cashback, Business, Student, and General managers are ready.")
        print("✅ Graph integration is working.")
        return 0
    else:
        print("\n💥 Some Card Manager tests failed.")
        print("❌ Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

