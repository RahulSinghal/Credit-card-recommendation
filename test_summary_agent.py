#!/usr/bin/env python3
"""
Test Summary Agent
Validates the Summary Agent in isolation before graph integration.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.state import GraphState, RequestParsed, Consent
from src.nodes.summary import SummaryAgent, SummaryResult, FinalRecommendation
from src.nodes.card_managers import CardRecommendation, ManagerResult
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


def test_summary_agent_creation():
    """Test that the summary agent can be created."""
    print("🧪 Testing Summary Agent Creation...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        summary_agent = SummaryAgent(mock_llm, mock_policy)
        
        assert summary_agent.agent_type == "summary"
        print("   ✅ Summary Agent created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Summary Agent creation failed: {str(e)}")
        return False


async def test_summary_agent_aggregation():
    """Test the summary agent's aggregation logic."""
    print("\n🧪 Testing Summary Agent Aggregation...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        summary_agent = SummaryAgent(mock_llm, mock_policy)
        
        # Create mock manager results
        mock_manager_results = {
            "travel_manager": ManagerResult(
                manager_type="travel_manager",
                recommendations=[
                    CardRecommendation(
                        card_id="travel_001",
                        card_name="Singapore Airlines KrisFlyer Credit Card",
                        card_type="travel",
                        issuer="DBS Bank",
                        annual_fee=192.60,
                        rewards_rate="1.2 miles per S$1",
                        signup_bonus="15,000 KrisFlyer miles",
                        credit_score_required="excellent",
                        pros=["High miles earning", "No foreign transaction fees"],
                        cons=["High annual fee"],
                        match_score=0.87,
                        reasoning="Excellent match for travel goals"
                    )
                ],
                total_cards_found=1,
                best_match=None,
                reasoning="Found travel cards",
                execution_time=0.001
            ),
            "cashback_manager": ManagerResult(
                manager_type="cashback_manager",
                recommendations=[
                    CardRecommendation(
                        card_id="cashback_001",
                        card_name="DBS Live Fresh Card",
                        card_type="cashback",
                        issuer="DBS Bank",
                        annual_fee=0,
                        rewards_rate="5% cashback on online spending",
                        signup_bonus="S$100 cashback",
                        credit_score_required="good",
                        pros=["No annual fee", "High online cashback"],
                        cons=["Limited offline benefits"],
                        match_score=1.00,
                        reasoning="Perfect cashback card"
                    )
                ],
                total_cards_found=1,
                best_match=None,
                reasoning="Found cashback cards",
                execution_time=0.001
            )
        }
        
        # Test aggregation
        all_cards = await summary_agent.aggregate_manager_results(mock_manager_results)
        print(f"   ✅ Aggregated {len(all_cards)} cards from managers")
        
        # Test overall score calculation
        overall_score = summary_agent.calculate_overall_score(all_cards[0], mock_manager_results)
        print(f"   ✅ Overall score calculated: {overall_score:.2f}")
        
        # Test best features identification
        test_request = RequestParsed(
            intent="recommend_card",
            goals=["miles", "cashback"],
            constraints={},
            jurisdiction="SG",
            risk_tolerance="standard",
            time_horizon="12m"
        )
        
        best_features = summary_agent.identify_best_features(all_cards[0], test_request)
        print(f"   ✅ Best features identified: {best_features}")
        
        # Test reasoning generation
        reasoning = summary_agent.generate_reasoning(all_cards[0], overall_score, best_features)
        print(f"   ✅ Reasoning generated: {reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Summary agent aggregation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_summary_agent_execution():
    """Test full summary agent execution with state."""
    print("\n🧪 Testing Summary Agent Execution...")
    
    try:
        mock_llm = MockLLMTool()
        mock_policy = MockPolicyTool()
        summary_agent = SummaryAgent(mock_llm, mock_policy)
        
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
                "travel_manager": ManagerResult(
                    manager_type="travel_manager",
                    recommendations=[
                        CardRecommendation(
                            card_id="travel_001",
                            card_name="Singapore Airlines KrisFlyer Credit Card",
                            card_type="travel",
                            issuer="DBS Bank",
                            annual_fee=192.60,
                            rewards_rate="1.2 miles per S$1",
                            signup_bonus="15,000 KrisFlyer miles",
                            credit_score_required="excellent",
                            pros=["High miles earning", "No foreign transaction fees"],
                            cons=["High annual fee"],
                            match_score=0.87,
                            reasoning="Excellent match for travel goals"
                        )
                    ],
                    total_cards_found=1,
                    best_match=None,
                    reasoning="Found travel cards",
                    execution_time=0.001
                )
            },
            final_recommendations=None,
            telemetry={"events": []},
            errors=[],
            current_node=None,
            completed_nodes=[],
            next_nodes=[]
        )
        
        # Execute the summary agent
        result_state = await summary_agent.execute(test_state)
        
        print(f"   ✅ Summary agent executed successfully")
        print(f"   ✅ Current node: {result_state.current_node}")
        print(f"   ✅ Completed nodes: {result_state.completed_nodes}")
        
        # Check results
        if result_state.final_recommendations:
            summary_result = result_state.final_recommendations
            print(f"   ✅ Summary result created")
            print(f"   ✅ Total cards analyzed: {summary_result.total_cards_analyzed}")
            print(f"   ✅ Final recommendations: {len(summary_result.final_recommendations)}")
            print(f"   ✅ Confidence score: {summary_result.confidence_score:.2f}")
            
            if summary_result.top_recommendation:
                top_rec = summary_result.top_recommendation
                print(f"   ✅ Top recommendation: {top_rec.card_name}")
                print(f"   ✅ Overall score: {top_rec.overall_score:.2f}")
                print(f"   ✅ Best for: {', '.join(top_rec.best_for)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Summary agent execution test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_summary_node_creation():
    """Test that the summary node can be created."""
    print("\n🧪 Testing Summary Node Creation...")
    
    try:
        from src.nodes.summary import create_summary_node
        
        summary_node = create_summary_node()
        
        # Test that it's callable
        assert callable(summary_node)
        print("   ✅ Summary node created successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Summary node creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all summary agent tests."""
    print("🚀 SUMMARY AGENT TESTING")
    print("=" * 60)
    
    # Test 1: Agent creation
    creation_success = test_summary_agent_creation()
    
    # Test 2: Aggregation logic
    aggregation_success = await test_summary_agent_aggregation()
    
    # Test 3: Full execution
    execution_success = await test_summary_agent_execution()
    
    # Test 4: Node creation
    node_success = await test_summary_node_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY AGENT TEST RESULTS")
    print("=" * 60)
    print(f"Agent Creation: {'✅ PASSED' if creation_success else '❌ FAILED'}")
    print(f"Aggregation Logic: {'✅ PASSED' if aggregation_success else '❌ FAILED'}")
    print(f"Full Execution: {'✅ PASSED' if execution_success else '❌ FAILED'}")
    print(f"Node Creation: {'✅ PASSED' if node_success else '❌ FAILED'}")
    
    overall_success = all([
        creation_success, aggregation_success, execution_success, node_success
    ])
    
    if overall_success:
        print("\n🎉 All Summary Agent tests passed!")
        print("✅ The Summary Agent is working correctly.")
        print("✅ Ready for graph integration.")
        return 0
    else:
        print("\n💥 Some Summary Agent tests failed.")
        print("❌ Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

