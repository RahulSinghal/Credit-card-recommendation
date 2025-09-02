#!/usr/bin/env python3
"""
Progressive LangGraph Test
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def progressive_test():
    """Progressive test to identify the issue."""
    print("🔍 Progressive LangGraph Test...")
    
    try:
        # Step 1: Basic imports
        print("✅ Step 1: Basic imports...")
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        from src.models.state import GraphState
        print("   ✅ All imports successful")
        
        # Step 2: Create basic graph
        print("✅ Step 2: Creating basic graph...")
        workflow = StateGraph(GraphState)
        print("   ✅ Basic graph created")
        
        # Step 3: Add extractor node
        print("✅ Step 3: Adding extractor node...")
        from src.nodes.extractor import create_extractor_node
        from src.tools.base import LLMTool, PolicyTool
        
        class MockLLMTool(LLMTool):
            async def execute(self, **kwargs):
                pass
            async def nlu_extract(self, text: str, schema: dict):
                return {
                    "intent": "recommend_card",
                    "goals": ["rewards"],
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
        
        mock_llm_tool = MockLLMTool()
        mock_policy_tool = MockPolicyTool()
        
        extractor_node = create_extractor_node(mock_llm_tool, mock_policy_tool)
        workflow.add_node("extractor", extractor_node)
        print("   ✅ Extractor node added")
        
        # Step 4: Add router node
        print("✅ Step 4: Adding router node...")
        
        async def router_node(state: GraphState) -> GraphState:
            state.current_node = "router"
            state.fanout_plan = ["travel_manager"]
            state.completed_nodes.append("router")
            state.next_nodes = []
            return state
        
        workflow.add_node("router", router_node)
        print("   ✅ Router node added")
        
        # Step 5: Add conditional edges
        print("✅ Step 5: Adding conditional edges...")
        
        def should_continue_to_router(state: GraphState) -> str:
            if state.errors:
                return "error_handler"
            return "router"
        
        workflow.add_conditional_edges(
            "extractor",
            should_continue_to_router,
            {
                "router": "router",
                END: END
            }
        )
        print("   ✅ Conditional edges added")
        
        # Step 6: Set entry point
        print("✅ Step 6: Setting entry point...")
        workflow.set_entry_point("extractor")
        print("   ✅ Entry point set")
        
        # Step 7: Compile
        print("✅ Step 7: Compiling graph...")
        app = workflow.compile(checkpointer=MemorySaver())
        print("   ✅ Graph compiled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Progressive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(progressive_test())
    print(f"\n🎯 Progressive test {'SUCCESSFUL' if success else 'FAILED'}")

