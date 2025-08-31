#!/usr/bin/env python3
"""
LangSmith Monitoring Integration for Credit Card Recommendation System
Provides comprehensive monitoring, tracing, and analytics for the multi-agent workflow.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from langsmith import Client, RunTree, traceable
    from langsmith.run_trees import RunTree
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("⚠️ LangSmith not available. Install with: pip install langsmith")

from src.models.state import GraphState, RequestParsed, FinalRecommendations

logger = logging.getLogger(__name__)


class LangSmithMonitor:
    """LangSmith monitoring wrapper for the credit card recommendation system."""
    
    def __init__(self):
        self.client = None
        self.project_name = os.getenv("LANGSMITH_PROJECT", "credit-card-recommendation")
        self.enabled = False
        
        if LANGSMITH_AVAILABLE:
            try:
                api_key = os.getenv("LANGSMITH_API_KEY")
                endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
                
                if api_key:
                    self.client = Client(api_key=api_key, api_url=endpoint)
                    self.enabled = True
                    logger.info(f"✅ LangSmith monitoring enabled for project: {self.project_name}")
                else:
                    logger.warning("⚠️ LANGSMITH_API_KEY not set. LangSmith monitoring disabled.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LangSmith: {e}")
    
    def create_run_tree(self, user_input: str, session_id: str) -> Optional[RunTree]:
        """Create a new run tree for tracking the entire workflow."""
        if not self.enabled or not self.client:
            return None
        
        try:
            run_tree = RunTree(
                name="credit_card_recommendation_workflow",
                run_type="chain",
                inputs={"user_input": user_input},
                session_id=session_id,
                project_name=self.project_name,
                tags=["credit-cards", "recommendation", "multi-agent"]
            )
            return run_tree
        except Exception as e:
            logger.error(f"❌ Failed to create run tree: {e}")
            return None
    
    def trace_node_execution(self, 
                           run_tree: RunTree, 
                           node_name: str, 
                           inputs: Dict[str, Any], 
                           outputs: Dict[str, Any],
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """Trace the execution of a specific node in the workflow."""
        if not self.enabled or not run_tree:
            return
        
        try:
            run_tree.add_child(
                name=node_name,
                run_type="tool",
                inputs=inputs,
                outputs=outputs,
                metadata=metadata or {},
                tags=[node_name, "credit-cards"]
            )
        except Exception as e:
            logger.error(f"❌ Failed to trace node {node_name}: {e}")
    
    def trace_llm_call(self, 
                       run_tree: RunTree, 
                       prompt: str, 
                       response: str, 
                       model: str,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Trace LLM calls for monitoring and analysis."""
        if not self.enabled or not run_tree:
            return
        
        try:
            run_tree.add_child(
                name="llm_call",
                run_type="llm",
                inputs={"prompt": prompt},
                outputs={"response": response},
                metadata={
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                },
                tags=["llm", "credit-cards"]
            )
        except Exception as e:
            logger.error(f"❌ Failed to trace LLM call: {e}")
    
    def trace_card_recommendation(self, 
                                 run_tree: RunTree, 
                                 card_name: str, 
                                 score: float, 
                                 reasoning: str,
                                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """Trace individual card recommendations for analysis."""
        if not self.enabled or not run_tree:
            return
        
        try:
            run_tree.add_child(
                name="card_recommendation",
                run_type="tool",
                inputs={"card_name": card_name},
                outputs={"score": score, "reasoning": reasoning},
                metadata={
                    "recommendation_type": "credit_card",
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                },
                tags=["recommendation", "credit-cards"]
            )
        except Exception as e:
            logger.error(f"❌ Failed to trace card recommendation: {e}")
    
    def trace_workflow_completion(self, 
                                 run_tree: RunTree, 
                                 final_state: GraphState,
                                 execution_time: float,
                                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """Trace the completion of the entire workflow."""
        if not self.enabled or not run_tree:
            return
        
        try:
            # Extract key metrics from final state
            total_cards = 0
            if final_state.final_recommendations:
                total_cards = final_state.final_recommendations.total_cards_analyzed
            
            run_tree.end(
                outputs={
                    "total_cards_analyzed": total_cards,
                    "execution_time": execution_time,
                    "final_recommendations_count": len(final_state.final_recommendations.final_recommendations) if final_state.final_recommendations else 0
                },
                metadata={
                    "workflow_completed": True,
                    "completion_timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Submit the run tree to LangSmith
            self.client.create_run_tree(run_tree)
            logger.info(f"✅ Workflow traced and submitted to LangSmith")
            
        except Exception as e:
            logger.error(f"❌ Failed to trace workflow completion: {e}")
    
    def get_workflow_analytics(self, 
                              start_date: Optional[datetime] = None, 
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Retrieve analytics and metrics from LangSmith."""
        if not self.enabled or not self.client:
            return {"error": "LangSmith not available"}
        
        try:
            # Get runs for the project
            runs = self.client.list_runs(
                project_name=self.project_name,
                start_time=start_date,
                end_time=end_date
            )
            
            # Calculate metrics
            total_runs = len(list(runs))
            successful_runs = sum(1 for run in runs if run.status == "completed")
            failed_runs = total_runs - successful_runs
            
            # Get average execution time
            execution_times = []
            for run in runs:
                if run.start_time and run.end_time:
                    execution_times.append((run.end_time - run.start_time).total_seconds())
            
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            return {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                "average_execution_time": avg_execution_time,
                "project_name": self.project_name
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get analytics: {e}")
            return {"error": str(e)}
    
    def get_node_performance_metrics(self, 
                                   node_name: str, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get performance metrics for a specific node."""
        if not self.enabled or not self.client:
            return {"error": "LangSmith not available"}
        
        try:
            runs = self.client.list_runs(
                project_name=self.project_name,
                start_time=start_date,
                end_time=end_date,
                tags=[node_name]
            )
            
            node_runs = list(runs)
            total_node_runs = len(node_runs)
            
            if total_node_runs == 0:
                return {"node_name": node_name, "total_runs": 0, "message": "No runs found for this node"}
            
            # Calculate node-specific metrics
            successful_node_runs = sum(1 for run in node_runs if run.status == "completed")
            failed_node_runs = total_node_runs - successful_node_runs
            
            # Get execution times for this node
            node_execution_times = []
            for run in node_runs:
                if run.start_time and run.end_time:
                    node_execution_times.append((run.end_time - run.start_time).total_seconds())
            
            avg_node_execution_time = sum(node_execution_times) / len(node_execution_times) if node_execution_times else 0
            
            return {
                "node_name": node_name,
                "total_runs": total_node_runs,
                "successful_runs": successful_node_runs,
                "failed_runs": failed_node_runs,
                "success_rate": (successful_node_runs / total_node_runs * 100) if total_node_runs > 0 else 0,
                "average_execution_time": avg_node_execution_time,
                "min_execution_time": min(node_execution_times) if node_execution_times else 0,
                "max_execution_time": max(node_execution_times) if node_execution_times else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get node metrics for {node_name}: {e}")
            return {"error": str(e)}


# Global monitor instance
langsmith_monitor = LangSmithMonitor()


def traceable_workflow(func):
    """Decorator to make workflow functions traceable with LangSmith."""
    if not LANGSMITH_AVAILABLE:
        return func
    
    @traceable(
        name="credit_card_workflow",
        project_name=os.getenv("LANGSMITH_PROJECT", "credit-card-recommendation"),
        tags=["credit-cards", "workflow"]
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    return wrapper


async def monitor_workflow_execution(user_input: str, 
                                   workflow_func, 
                                   *args, 
                                   **kwargs) -> Any:
    """Monitor and trace the execution of a workflow function."""
    if not langsmith_monitor.enabled:
        # If LangSmith is not available, just run the workflow normally
        return await workflow_func(*args, **kwargs)
    
    start_time = datetime.now()
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create run tree for this workflow execution
    run_tree = langsmith_monitor.create_run_tree(user_input, session_id)
    
    try:
        # Execute the workflow
        result = await workflow_func(*args, **kwargs)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Trace workflow completion
        if hasattr(result, 'final_recommendations'):
            langsmith_monitor.trace_workflow_completion(
                run_tree, 
                result, 
                execution_time,
                {"workflow_type": "credit_card_recommendation"}
            )
        
        return result
        
    except Exception as e:
        # Trace error if it occurs
        if run_tree:
            run_tree.end(
                error=str(e),
                metadata={"error": True, "error_timestamp": datetime.now().isoformat()}
            )
            try:
                langsmith_monitor.client.create_run_tree(run_tree)
            except:
                pass
        
        logger.error(f"❌ Workflow execution failed: {e}")
        raise


# Example usage functions
async def get_system_analytics():
    """Get comprehensive system analytics from LangSmith."""
    return langsmith_monitor.get_workflow_analytics()

async def get_node_metrics(node_name: str):
    """Get performance metrics for a specific node."""
    return langsmith_monitor.get_node_performance_metrics(node_name)

async def get_recent_workflows(limit: int = 10):
    """Get recent workflow executions."""
    if not langsmith_monitor.enabled or not langsmith_monitor.client:
        return {"error": "LangSmith not available"}
    
    try:
        runs = langsmith_monitor.client.list_runs(
            project_name=langsmith_monitor.project_name,
            limit=limit
        )
        
        recent_workflows = []
        for run in runs:
            recent_workflows.append({
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "end_time": run.end_time.isoformat() if run.end_time else None,
                "execution_time": (run.end_time - run.start_time).total_seconds() if run.start_time and run.end_time else None
            })
        
        return {"recent_workflows": recent_workflows}
        
    except Exception as e:
        logger.error(f"❌ Failed to get recent workflows: {e}")
        return {"error": str(e)}
