#!/usr/bin/env python3
"""
LangSmith Monitoring Demo for Credit Card Recommendation System
Shows how to use LangSmith for monitoring, tracing, and analytics.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.langsmith_monitoring import (
    langsmith_monitor, 
    monitor_workflow_execution,
    get_system_analytics,
    get_node_metrics,
    get_recent_workflows
)
from src.graph.credit_card_graph import create_credit_card_graph, create_initial_state
from src.tools.mock_tools import MockLLMTool, MockPolicyTool


async def demo_langsmith_monitoring():
    """Demonstrate LangSmith monitoring capabilities."""
    print("🚀 LangSmith Monitoring Demo for Credit Card Recommendation System")
    print("=" * 80)
    
    # Check LangSmith status
    if langsmith_monitor.enabled:
        print(f"✅ LangSmith monitoring is ENABLED")
        print(f"   Project: {langsmith_monitor.project_name}")
        print(f"   Client: {langsmith_monitor.client}")
    else:
        print("⚠️ LangSmith monitoring is DISABLED")
        print("   Set LANGSMITH_API_KEY environment variable to enable")
        print("   Get your API key from: https://smith.langchain.com/")
    
    print()
    
    # Demo 1: Run a monitored workflow
    print("🔄 Demo 1: Running Monitored Workflow")
    print("-" * 50)
    
    try:
        # Create the graph
        llm_tool = MockLLMTool(use_openai=True)
        policy_tool = MockPolicyTool()
        graph = create_credit_card_graph(llm_tool, policy_tool)
        
        # Test user input
        user_input = "I want a travel credit card with lounge access and travel insurance"
        print(f"   User Input: {user_input}")
        
        # Run the workflow with monitoring
        result = await monitor_workflow_execution(
            user_input=user_input,
            workflow_func=graph.ainvoke,
            create_initial_state(user_input)
        )
        
        print(f"   ✅ Workflow completed successfully")
        if hasattr(result, 'final_recommendations') and result.final_recommendations:
            final_recs = result.final_recommendations
            print(f"   📊 Generated {len(final_recs.final_recommendations)} recommendations")
            print(f"   🎯 Top card: {final_recs.top_recommendation.card_name if final_recs.top_recommendation else 'None'}")
        
    except Exception as e:
        print(f"   ❌ Workflow failed: {e}")
    
    print()
    
    # Demo 2: Get system analytics
    print("📊 Demo 2: System Analytics")
    print("-" * 50)
    
    try:
        analytics = await get_system_analytics()
        if "error" not in analytics:
            print(f"   📈 Total Runs: {analytics['total_runs']}")
            print(f"   ✅ Successful: {analytics['successful_runs']}")
            print(f"   ❌ Failed: {analytics['failed_runs']}")
            print(f"   🎯 Success Rate: {analytics['success_rate']:.1f}%")
            print(f"   ⏱️ Avg Execution Time: {analytics['average_execution_time']:.2f}s")
        else:
            print(f"   ⚠️ {analytics['error']}")
    except Exception as e:
        print(f"   ❌ Failed to get analytics: {e}")
    
    print()
    
    # Demo 3: Get node performance metrics
    print("🔍 Demo 3: Node Performance Metrics")
    print("-" * 50)
    
    nodes_to_check = ["extractor", "travel_manager", "summary"]
    for node_name in nodes_to_check:
        try:
            metrics = await get_node_metrics(node_name)
            if "error" not in metrics:
                print(f"   📊 {node_name}:")
                print(f"      Total Runs: {metrics['total_runs']}")
                print(f"      Success Rate: {metrics['success_rate']:.1f}%")
                print(f"      Avg Time: {metrics['average_execution_time']:.2f}s")
            else:
                print(f"   ⚠️ {node_name}: {metrics['error']}")
        except Exception as e:
            print(f"   ❌ {node_name}: Failed to get metrics - {e}")
    
    print()
    
    # Demo 4: Get recent workflows
    print("📋 Demo 4: Recent Workflows")
    print("-" * 50)
    
    try:
        recent = await get_recent_workflows(limit=5)
        if "error" not in recent:
            workflows = recent['recent_workflows']
            if workflows:
                for i, workflow in enumerate(workflows[:3]):  # Show first 3
                    print(f"   {i+1}. {workflow['name']}")
                    print(f"      Status: {workflow['status']}")
                    print(f"      Time: {workflow['execution_time']:.2f}s" if workflow['execution_time'] else "      Time: N/A")
            else:
                print("   📭 No recent workflows found")
        else:
            print(f"   ⚠️ {recent['error']}")
    except Exception as e:
        print(f"   ❌ Failed to get recent workflows: {e}")
    
    print()
    
    # Demo 5: Manual tracing example
    print("🎯 Demo 5: Manual Tracing Example")
    print("-" * 50)
    
    if langsmith_monitor.enabled:
        try:
            # Create a run tree manually
            run_tree = langsmith_monitor.create_run_tree(
                "Manual test query", 
                f"manual_session_{datetime.now().strftime('%H%M%S')}"
            )
            
            if run_tree:
                # Trace some operations
                langsmith_monitor.trace_node_execution(
                    run_tree,
                    "manual_test_node",
                    {"input": "test input"},
                    {"output": "test output"},
                    {"test_type": "manual_demo"}
                )
                
                langsmith_monitor.trace_llm_call(
                    run_tree,
                    "What is a credit card?",
                    "A credit card is a payment card...",
                    "gpt-4o-mini",
                    {"demo": True}
                )
                
                # End the run
                run_tree.end(
                    outputs={"manual_test_completed": True},
                    metadata={"demo": True, "timestamp": datetime.now().isoformat()}
                )
                
                # Submit to LangSmith
                langsmith_monitor.client.create_run_tree(run_tree)
                print("   ✅ Manual tracing completed and submitted to LangSmith")
            else:
                print("   ⚠️ Failed to create run tree")
                
        except Exception as e:
            print(f"   ❌ Manual tracing failed: {e}")
    else:
        print("   ⚠️ LangSmith not available for manual tracing")
    
    print()
    print("🎉 LangSmith Monitoring Demo Completed!")
    
    # Summary
    if langsmith_monitor.enabled:
        print("\n📋 Next Steps:")
        print("   1. Visit https://smith.langchain.com/ to view your traces")
        print("   2. Set up alerts and monitoring dashboards")
        print("   3. Analyze performance patterns and optimize your workflow")
        print("   4. Use the analytics for business insights")
    else:
        print("\n📋 To Enable LangSmith:")
        print("   1. Get your API key from https://smith.langchain.com/")
        print("   2. Set environment variable: LANGSMITH_API_KEY=your_key_here")
        print("   3. Restart your application")
        print("   4. Run this demo again")


async def demo_environment_setup():
    """Show how to set up LangSmith environment."""
    print("🔧 LangSmith Environment Setup Guide")
    print("=" * 80)
    
    print("1. Get your LangSmith API key:")
    print("   - Visit: https://smith.langchain.com/")
    print("   - Sign up or log in")
    print("   - Go to API Keys section")
    print("   - Create a new API key")
    print()
    
    print("2. Set environment variables:")
    print("   Windows (PowerShell):")
    print("   $env:LANGSMITH_API_KEY='your_api_key_here'")
    print("   $env:LANGSMITH_PROJECT='credit-card-recommendation'")
    print()
    print("   Windows (Command Prompt):")
    print("   set LANGSMITH_API_KEY=your_api_key_here")
    print("   set LANGSMITH_PROJECT=credit-card-recommendation")
    print()
    print("   Linux/Mac:")
    print("   export LANGSMITH_API_KEY='your_api_key_here'")
    print("   export LANGSMITH_PROJECT='credit-card-recommendation'")
    print()
    
    print("3. Or create a .env file:")
    print("   LANGSMITH_API_KEY=your_api_key_here")
    print("   LANGSMITH_PROJECT=credit-card-recommendation")
    print("   LANGSMITH_ENDPOINT=https://api.smith.langchain.com")
    print("   LANGSMITH_TRACING_V2=true")
    print()
    
    print("4. Install LangSmith:")
    print("   pip install langsmith")
    print()
    
    print("5. Restart your application and run the demo!")


async def main():
    """Main demo function."""
    print("🚀 LangSmith Monitoring Demo")
    print("=" * 80)
    
    # Check if user wants setup guide
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        await demo_environment_setup()
        return
    
    # Run the main demo
    await demo_langsmith_monitoring()


if __name__ == "__main__":
    asyncio.run(main())

