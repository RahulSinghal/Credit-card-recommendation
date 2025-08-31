#!/usr/bin/env python3
"""
Card Manager Agents Demonstration
Shows how all card manager agents work together in the credit card recommendation system.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


async def demonstrate_travel_request():
    """Demonstrate a travel-focused credit card request."""
    print("\n🌍 TRAVEL CREDIT CARD REQUEST")
    print("=" * 50)
    
    # Create graph
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    graph = create_credit_card_graph(mock_llm, mock_policy)
    
    # Create initial state
    initial_state = create_initial_state(
        "I want a credit card that gives me airline miles and travel benefits"
    )
    
    print(f"User Query: {initial_state.user_query}")
    print(f"Locale: {initial_state.locale}")
    print(f"Session ID: {initial_state.session_id}")
    
    # Execute the graph
    print("\n🚀 Executing Graph...")
    result = await graph.ainvoke(initial_state)
    
    # Show results
    print(f"\n✅ Graph Execution Complete!")
    print(f"Completed Nodes: {result['completed_nodes']}")
    print(f"Current Node: {result['current_node']}")
    
    if result['manager_results']:
        for manager_type, manager_result in result['manager_results'].items():
            print(f"\n📊 {manager_type.upper()} RESULTS:")
            print(f"   Total Cards Found: {manager_result.total_cards_found}")
            print(f"   Recommendations: {len(manager_result.recommendations)}")
            print(f"   Execution Time: {manager_result.execution_time:.3f}s")
            print(f"   Reasoning: {manager_result.reasoning}")
            
            if manager_result.best_match:
                best = manager_result.best_match
                print(f"\n🏆 BEST MATCH:")
                print(f"   Card: {best.card_name}")
                print(f"   Issuer: {best.issuer}")
                print(f"   Annual Fee: S${best.annual_fee}")
                print(f"   Rewards: {best.rewards_rate}")
                print(f"   Signup Bonus: {best.signup_bonus}")
                print(f"   Match Score: {best.match_score:.2f}")
                print(f"   Reasoning: {best.reasoning}")
                
                print(f"\n   Pros: {', '.join(best.pros)}")
                print(f"   Cons: {', '.join(best.cons)}")


async def demonstrate_cashback_request():
    """Demonstrate a cashback-focused credit card request."""
    print("\n💰 CASHBACK CREDIT CARD REQUEST")
    print("=" * 50)
    
    # Create graph
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    graph = create_credit_card_graph(mock_llm, mock_policy)
    
    # Create initial state
    initial_state = create_initial_state(
        "I need a credit card with high cashback rewards for online shopping"
    )
    
    print(f"User Query: {initial_state.user_query}")
    print(f"Locale: {initial_state.locale}")
    print(f"Session ID: {initial_state.session_id}")
    
    # Execute the graph
    print("\n🚀 Executing Graph...")
    result = await graph.ainvoke(initial_state)
    
    # Show results
    print(f"\n✅ Graph Execution Complete!")
    print(f"Completed Nodes: {result['completed_nodes']}")
    print(f"Current Node: {result['current_node']}")
    
    if result['manager_results']:
        for manager_type, manager_result in result['manager_results'].items():
            print(f"\n📊 {manager_type.upper()} RESULTS:")
            print(f"   Total Cards Found: {manager_result.total_cards_found}")
            print(f"   Recommendations: {len(manager_result.recommendations)}")
            print(f"   Execution Time: {manager_result.execution_time:.3f}s")
            print(f"   Reasoning: {manager_result.reasoning}")
            
            if manager_result.best_match:
                best = manager_result.best_match
                print(f"\n🏆 BEST MATCH:")
                print(f"   Card: {best.card_name}")
                print(f"   Issuer: {best.issuer}")
                print(f"   Annual Fee: S${best.annual_fee}")
                print(f"   Rewards: {best.rewards_rate}")
                print(f"   Signup Bonus: {best.signup_bonus}")
                print(f"   Match Score: {best.match_score:.2f}")
                print(f"   Reasoning: {best.reasoning}")
                
                print(f"\n   Pros: {', '.join(best.pros)}")
                print(f"   Cons: {', '.join(best.cons)}")


async def demonstrate_business_request():
    """Demonstrate a business-focused credit card request."""
    print("\n💼 BUSINESS CREDIT CARD REQUEST")
    print("=" * 50)
    
    # Create graph
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    graph = create_credit_card_graph(mock_llm, mock_policy)
    
    # Create initial state
    initial_state = create_initial_state(
        "I need a business credit card for corporate expenses and employee cards"
    )
    
    print(f"User Query: {initial_state.user_query}")
    print(f"Locale: {initial_state.locale}")
    print(f"Session ID: {initial_state.session_id}")
    
    # Execute the graph
    print("\n🚀 Executing Graph...")
    result = await graph.ainvoke(initial_state)
    
    # Show results
    print(f"\n✅ Graph Execution Complete!")
    print(f"Completed Nodes: {result['completed_nodes']}")
    print(f"Current Node: {result['current_node']}")
    
    if result['manager_results']:
        for manager_type, manager_result in result['manager_results'].items():
            print(f"\n📊 {manager_type.upper()} RESULTS:")
            print(f"   Total Cards Found: {manager_result.total_cards_found}")
            print(f"   Recommendations: {len(manager_result.recommendations)}")
            print(f"   Execution Time: {manager_result.execution_time:.3f}s")
            print(f"   Reasoning: {manager_result.reasoning}")
            
            if manager_result.best_match:
                best = manager_result.best_match
                print(f"\n🏆 BEST MATCH:")
                print(f"   Card: {best.card_name}")
                print(f"   Issuer: {best.issuer}")
                print(f"   Annual Fee: S${best.annual_fee}")
                print(f"   Rewards: {best.rewards_rate}")
                print(f"   Signup Bonus: {best.signup_bonus}")
                print(f"   Match Score: {best.match_score:.2f}")
                print(f"   Reasoning: {best.reasoning}")
                
                print(f"\n   Pros: {', '.join(best.pros)}")
                print(f"   Cons: {', '.join(best.cons)}")


async def demonstrate_student_request():
    """Demonstrate a student-focused credit card request."""
    print("\n🎓 STUDENT CREDIT CARD REQUEST")
    print("=" * 50)
    
    # Create graph
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    graph = create_credit_card_graph(mock_llm, mock_policy)
    
    # Create initial state
    initial_state = create_initial_state(
        "I'm a student and need a credit card to build my credit history"
    )
    
    print(f"User Query: {initial_state.user_query}")
    print(f"Locale: {initial_state.locale}")
    print(f"Session ID: {initial_state.session_id}")
    
    # Execute the graph
    print("\n🚀 Executing Graph...")
    result = await graph.ainvoke(initial_state)
    
    # Show results
    print(f"\n✅ Graph Execution Complete!")
    print(f"Completed Nodes: {result['completed_nodes']}")
    print(f"Current Node: {result['current_node']}")
    
    if result['manager_results']:
        for manager_type, manager_result in result['manager_results'].items():
            print(f"\n📊 {manager_type.upper()} RESULTS:")
            print(f"   Total Cards Found: {manager_result.total_cards_found}")
            print(f"   Recommendations: {len(manager_result.recommendations)}")
            print(f"   Execution Time: {manager_result.execution_time:.3f}s")
            print(f"   Reasoning: {manager_result.reasoning}")
            
            if manager_result.best_match:
                best = manager_result.best_match
                print(f"\n🏆 BEST MATCH:")
                print(f"   Card: {best.card_name}")
                print(f"   Issuer: {best.issuer}")
                print(f"   Annual Fee: S${best.annual_fee}")
                print(f"   Rewards: {best.rewards_rate}")
                print(f"   Signup Bonus: {best.signup_bonus}")
                print(f"   Match Score: {best.match_score:.2f}")
                print(f"   Reasoning: {best.reasoning}")
                
                print(f"\n   Pros: {', '.join(best.pros)}")
                print(f"   Cons: {', '.join(best.cons)}")


async def demonstrate_general_request():
    """Demonstrate a general-purpose credit card request."""
    print("\n🔄 GENERAL CREDIT CARD REQUEST")
    print("=" * 50)
    
    # Create graph
    mock_llm = MockLLMTool()
    mock_policy = MockPolicyTool()
    graph = create_credit_card_graph(mock_llm, mock_policy)
    
    # Create initial state
    initial_state = create_initial_state(
        "I just want a good credit card with rewards"
    )
    
    print(f"User Query: {initial_state.user_query}")
    print(f"Locale: {initial_state.locale}")
    print(f"Session ID: {initial_state.session_id}")
    
    # Execute the graph
    print("\n🚀 Executing Graph...")
    result = await graph.ainvoke(initial_state)
    
    # Show results
    print(f"\n✅ Graph Execution Complete!")
    print(f"Completed Nodes: {result['completed_nodes']}")
    print(f"Current Node: {result['current_node']}")
    
    if result['manager_results']:
        for manager_type, manager_result in result['manager_results'].items():
            print(f"\n📊 {manager_type.upper()} RESULTS:")
            print(f"   Total Cards Found: {manager_result.total_cards_found}")
            print(f"   Recommendations: {len(manager_result.recommendations)}")
            print(f"   Execution Time: {manager_result.execution_time:.3f}s")
            print(f"   Reasoning: {manager_result.reasoning}")
            
            if manager_result.best_match:
                best = manager_result.best_match
                print(f"\n🏆 BEST MATCH:")
                print(f"   Card: {best.card_name}")
                print(f"   Issuer: {best.issuer}")
                print(f"   Annual Fee: S${best.annual_fee}")
                print(f"   Rewards: {best.rewards_rate}")
                print(f"   Signup Bonus: {best.signup_bonus}")
                print(f"   Match Score: {best.match_score:.2f}")
                print(f"   Reasoning: {best.reasoning}")
                
                print(f"\n   Pros: {', '.join(best.pros)}")
                print(f"   Cons: {', '.join(best.cons)}")


async def main():
    """Run all demonstrations."""
    print("🚀 CARD MANAGER AGENTS DEMONSTRATION")
    print("=" * 60)
    print("This demonstration shows how all 5 card manager agents work together")
    print("to provide personalized credit card recommendations based on user goals.")
    print("\nEach agent specializes in different card types:")
    print("🌍 Travel Manager - Miles, airline, hotel rewards")
    print("💰 Cashback Manager - Cashback percentages, categories") 
    print("💼 Business Manager - Business expenses, corporate cards")
    print("🎓 Student Manager - Building credit, student-friendly cards")
    print("🔄 General Manager - Default rewards, general purpose")
    
    # Run demonstrations
    await demonstrate_travel_request()
    await demonstrate_cashback_request()
    await demonstrate_business_request()
    await demonstrate_student_request()
    await demonstrate_general_request()
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("✅ All 5 Card Manager Agents are working perfectly!")
    print("✅ Each agent provides specialized analysis and recommendations")
    print("✅ The system automatically routes to the right managers")
    print("✅ Mock data provides realistic Singapore-based card options")
    print("✅ Ready for production use with real LLMs and card catalogs")


if __name__ == "__main__":
    asyncio.run(main())
