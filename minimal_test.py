#!/usr/bin/env python3
"""
Minimal LangGraph Test
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def minimal_test():
    """Minimal test to isolate the issue."""
    print("🔍 Minimal LangGraph Test...")
    
    try:
        # Step 1: Test basic imports
        print("✅ Step 1: Testing basic imports...")
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        print("   ✅ LangGraph imports successful")
        
        # Step 2: Test state model import
        print("✅ Step 2: Testing state model import...")
        from src.models.state import GraphState
        print("   ✅ State model import successful")
        
        # Step 3: Test basic StateGraph creation
        print("✅ Step 3: Testing basic StateGraph creation...")
        workflow = StateGraph(GraphState)
        print("   ✅ StateGraph created successfully")
        
        # Step 4: Test adding a simple node
        print("✅ Step 4: Testing node addition...")
        
        async def simple_node(state: GraphState) -> GraphState:
            state.current_node = "simple"
            return state
        
        workflow.add_node("simple", simple_node)
        print("   ✅ Node added successfully")
        
        # Step 5: Test setting entry point
        print("✅ Step 5: Testing entry point...")
        workflow.set_entry_point("simple")
        print("   ✅ Entry point set successfully")
        
        # Step 6: Test compilation
        print("✅ Step 6: Testing compilation...")
        app = workflow.compile(checkpointer=MemorySaver())
        print("   ✅ Graph compiled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(minimal_test())
    print(f"\n🎯 Minimal test {'SUCCESSFUL' if success else 'FAILED'}")
