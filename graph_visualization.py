#!/usr/bin/env python3
"""
LangGraph Structure Visualization
Shows the current graph structure and explains how it works.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def visualize_graph_structure():
    """Visualize the current LangGraph structure."""
    print("🔍 CREDIT CARD RECOMMENDATION GRAPH STRUCTURE")
    print("=" * 60)
    
    print("\n📊 GRAPH OVERVIEW:")
    print("   Entry Point: extractor")
    print("   Flow: extractor → router → END")
    print("   State Management: LangGraph StateGraph with Pydantic models")
    
    print("\n🏗️  NODE ARCHITECTURE:")
    print("   ┌─────────────────┐")
    print("   │   EXTRACTOR     │  ← Entry Point")
    print("   │   (Node 1)      │")
    print("   └─────────┬───────┘")
    print("             │")
    print("             ▼")
    print("   ┌─────────────────┐")
    print("   │   CONDITIONAL   │  ← Routing Logic")
    print("   │     EDGES       │")
    print("   └─────────┬───────┘")
    print("             │")
    print("             ▼")
    print("   ┌─────────────────┐")
    print("   │    ROUTER       │  ← Decision Node")
    print("   │   (Node 2)      │")
    print("   └─────────┬───────┘")
    print("             │")
    print("             ▼")
    print("   ┌─────────────────┐")
    print("   │      END        │  ← Graph Completion")
    print("   └─────────────────┘")
    
    print("\n🔧 NODE DETAILS:")
    
    print("\n   1️⃣  EXTRACTOR NODE:")
    print("      Purpose: Parse free-text into structured RequestParsed object")
    print("      Inputs: user_query, locale, consent")
    print("      Outputs: RequestParsed with goals, constraints, jurisdiction")
    print("      Tools: LLM Tool (OpenAI or Mock) + Policy Tool")
    print("      Fallback: Keyword-based parsing if LLM fails")
    
    print("\n   2️⃣  ROUTER NODE:")
    print("      Purpose: Analyze request and plan manager agent execution")
    print("      Inputs: Parsed request from Extractor")
    print("      Outputs: fanout_plan (which managers to call)")
    print("      Logic: Goal-based routing (travel, cashback, business, student)")
    
    print("\n📋 STATE MANAGEMENT:")
    print("   GraphState (Pydantic Model):")
    print("   ├── Session Info: session_id, user_query, locale")
    print("   ├── User Consent: personalization, data_sharing, credit_pull")
    print("   ├── Processing: request, policy_pack, catalog_meta")
    print("   ├── Orchestration: fanout_plan, manager_results, final_recommendations")
    print("   ├── Observability: telemetry, errors")
    print("   └── Execution: current_node, completed_nodes, next_nodes")
    
    print("\n🔄 EXECUTION FLOW:")
    print("   1. User submits credit card request")
    print("   2. Extractor Node parses text → RequestParsed object")
    print("   3. Router Node analyzes request → creates fanout_plan")
    print("   4. Graph ends (managers not implemented yet)")
    
    print("\n🎯 CONDITIONAL ROUTING:")
    print("   Extractor → Router: Always (unless errors)")
    print("   Router → END: Always (for now)")
    print("   Error Handling: Errors logged in state, graph continues")
    
    print("\n🚧 WHAT'S NOT IMPLEMENTED YET:")
    print("   ❌ Card Manager Agents (Travel, Cashback, Business, Student)")
    print("   ❌ Summary Agent")
    print("   ❌ Support Agents (Online Search, Policy)")
    print("   ❌ Error Handler Node")
    print("   ❌ Manager → Summary routing")
    
    print("\n✅ WHAT'S WORKING:")
    print("   ✅ LangGraph framework integration")
    print("   ✅ State management with Pydantic")
    print("   ✅ Extractor Node with LLM integration")
    print("   ✅ Router Node with goal-based analysis")
    print("   ✅ Conditional edge routing")
    print("   ✅ Graph compilation and execution")

async def demonstrate_graph_execution():
    """Demonstrate how the graph actually executes."""
    print("\n🧪 GRAPH EXECUTION DEMONSTRATION")
    print("=" * 60)
    
    try:
        from src.graph import create_credit_card_graph, create_initial_state
        from src.tools.base import LLMTool, PolicyTool
        
        # Create mock tools
        class MockLLMTool(LLMTool):
            async def execute(self, **kwargs):
                pass
            async def nlu_extract(self, text: str, schema: dict):
                text_lower = text.lower()
                goals = []
                if any(word in text_lower for word in ["miles", "travel"]):
                    goals.extend(["miles", "travel"])
                if any(word in text_lower for word in ["cashback"]):
                    goals.append("cashback")
                
                return {
                    "intent": "recommend_card",
                    "goals": goals if goals else ["rewards"],
                    "constraints": {},
                    "jurisdiction": "SG",
                    "risk_tolerance": "standard",
                    "time_horizon": "12m",
                    "confidence": 0.8
                }
            async def explainer(self, card_list, request):
                return "Mock explanation"
        
        class MockPolicyTool(PolicyTool):
            async def execute(self, **kwargs):
                pass
            async def lint_final(self, recos, policy):
                return type('MockPolicyReport', (), {'errors': [], 'warnings': []})()
        
        print("✅ Creating graph with mock tools...")
        graph = create_credit_card_graph(MockLLMTool(), MockPolicyTool())
        
        print("✅ Testing with sample query...")
        initial_state = create_initial_state(
            user_query="I want a travel credit card with lounge access",
            locale="en-SG"
        )
        
        print(f"   📝 Initial State Keys: {list(initial_state.dict().keys())}")
        print(f"   🎯 User Query: {initial_state.user_query}")
        print(f"   🌍 Locale: {initial_state.locale}")
        print(f"   ✅ Consent: {initial_state.consent.dict()}")
        
        print("\n✅ Executing graph...")
        config = {"configurable": {"thread_id": "demo"}}
        result = await graph.ainvoke(initial_state, config)
        
        print("\n📊 EXECUTION RESULTS:")
        print(f"   🎯 Request Intent: {result['request'].intent}")
        print(f"   🎯 Request Goals: {result['request'].goals}")
        print(f"   🌍 Jurisdiction: {result['request'].jurisdiction}")
        print(f"   📍 Current Node: {result['current_node']}")
        print(f"   ✅ Completed Nodes: {result['completed_nodes']}")
        print(f"   🚀 Fanout Plan: {result['fanout_plan']}")
        print(f"   📊 Telemetry Events: {len(result['telemetry'].get('events', []))}")
        print(f"   ❌ Errors: {len(result['errors'])}")
        
        print("\n🎉 Graph execution successful!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function to show graph structure and execution."""
    print("🚀 LANGGRAPH STRUCTURE & EXECUTION ANALYSIS")
    print("=" * 60)
    
    # Show structure
    visualize_graph_structure()
    
    # Demonstrate execution
    success = await demonstrate_graph_execution()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ LangGraph integration is working correctly!")
        print("✅ The system is ready for the next phase of development.")
        print("✅ Next step: Implement Card Manager Agents")
    else:
        print("❌ There are issues with the current implementation.")
        print("❌ Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
