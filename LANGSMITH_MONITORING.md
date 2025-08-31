# LangSmith Monitoring for Credit Card Recommendation System

This guide explains how to use LangSmith for comprehensive monitoring, tracing, and analytics of your credit card recommendation system.

## 🚀 What is LangSmith?

LangSmith is LangChain's official monitoring and observability platform that provides:

- **Workflow Tracing**: Track the execution of your multi-agent workflow
- **Performance Metrics**: Monitor execution times, success rates, and bottlenecks
- **LLM Call Monitoring**: Analyze OpenAI API usage and response quality
- **Error Tracking**: Identify and debug issues in your workflow
- **Analytics Dashboard**: Visualize system performance and usage patterns

## 📋 Prerequisites

1. **LangSmith Account**: Sign up at [https://smith.langchain.com/](https://smith.langchain.com/)
2. **API Key**: Get your API key from the LangSmith dashboard
3. **Python Package**: Install LangSmith with `pip install langsmith`

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install langsmith
```

### 2. Environment Variables

Set these environment variables:

```bash
# Windows PowerShell
$env:LANGSMITH_API_KEY='your_api_key_here'
$env:LANGSMITH_PROJECT='credit-card-recommendation'
$env:LANGSMITH_ENDPOINT='https://api.smith.langchain.com'
$env:LANGSMITH_TRACING_V2='true'

# Windows Command Prompt
set LANGSMITH_API_KEY=your_api_key_here
set LANGSMITH_PROJECT=credit-card-recommendation
set LANGSMITH_ENDPOINT=https://api.smith.langchain.com
set LANGSMITH_TRACING_V2=true

# Linux/Mac
export LANGSMITH_API_KEY='your_api_key_here'
export LANGSMITH_PROJECT='credit-card-recommendation'
export LANGSMITH_ENDPOINT='https://api.smith.langchain.com'
export LANGSMITH_TRACING_V2='true'
```

### 3. .env File (Alternative)

Create a `.env` file in your project root:

```env
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_PROJECT=credit-card-recommendation
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING_V2=true
```

## 🎯 Features

### Automatic Workflow Tracing

The system automatically traces:
- **Input Processing**: User queries and extracted information
- **Node Execution**: Each step in the multi-agent workflow
- **LLM Calls**: OpenAI API requests and responses
- **Card Recommendations**: Individual credit card suggestions
- **Workflow Completion**: Final results and execution metrics

### Performance Monitoring

Track:
- **Execution Times**: How long each node takes
- **Success Rates**: Percentage of successful operations
- **Error Patterns**: Common failure points
- **Resource Usage**: API calls and computational costs

### Analytics Dashboard

View:
- **Workflow Overview**: Complete execution traces
- **Node Performance**: Individual component metrics
- **Trend Analysis**: Performance over time
- **Error Reports**: Detailed failure analysis

## 🚀 Usage Examples

### Basic Monitoring

```python
from src.tools.langsmith_monitoring import monitor_workflow_execution

# Run workflow with automatic monitoring
result = await monitor_workflow_execution(
    user_input="I want a travel credit card",
    workflow_func=graph.ainvoke,
    initial_state
)
```

### Get Analytics

```python
from src.tools.langsmith_monitoring import get_system_analytics, get_node_metrics

# System-wide analytics
analytics = await get_system_analytics()
print(f"Success Rate: {analytics['success_rate']:.1f}%")

# Node-specific metrics
node_metrics = await get_node_metrics("travel_manager")
print(f"Travel Manager Avg Time: {node_metrics['average_execution_time']:.2f}s")
```

### Manual Tracing

```python
from src.tools.langsmith_monitoring import langsmith_monitor

# Create a custom trace
run_tree = langsmith_monitor.create_run_tree("Custom query", "session_123")

# Add custom operations
langsmith_monitor.trace_node_execution(
    run_tree,
    "custom_node",
    {"input": "test"},
    {"output": "result"},
    {"custom": True}
)

# Submit to LangSmith
langsmith_monitor.client.create_run_tree(run_tree)
```

## 📊 Demo Script

Run the demo to see LangSmith in action:

```bash
# Run the main demo
python demo_langsmith_monitoring.py

# Show setup instructions
python demo_langsmith_monitoring.py --setup
```

## 🔍 Monitoring Dashboard

### 1. Visit LangSmith Dashboard

Go to [https://smith.langchain.com/](https://smith.langchain.com/) and log in.

### 2. View Your Project

- Navigate to the "credit-card-recommendation" project
- See all workflow executions
- View performance metrics and trends

### 3. Analyze Traces

- **Timeline View**: See the complete workflow execution
- **Node Details**: Click on individual nodes for detailed metrics
- **Error Analysis**: Identify and debug issues
- **Performance Insights**: Find bottlenecks and optimization opportunities

## 📈 Key Metrics to Monitor

### Workflow Level
- **Total Executions**: Number of credit card recommendation requests
- **Success Rate**: Percentage of successful recommendations
- **Average Execution Time**: Overall system performance
- **Error Frequency**: Common failure patterns

### Node Level
- **Extractor Node**: Query parsing success rate
- **Router Node**: Correct routing accuracy
- **Card Managers**: Recommendation quality and speed
- **Summary Node**: Final output generation time

### LLM Level
- **API Response Times**: OpenAI API performance
- **Token Usage**: Cost optimization opportunities
- **Response Quality**: Relevance and accuracy metrics

## 🚨 Alerts and Notifications

Set up alerts for:
- **High Error Rates**: When success rate drops below threshold
- **Slow Performance**: When execution time exceeds limits
- **API Failures**: When OpenAI API calls fail
- **Resource Usage**: When costs exceed budget

## 🔧 Troubleshooting

### Common Issues

1. **LangSmith Not Enabled**
   - Check `LANGSMITH_API_KEY` environment variable
   - Verify API key is valid
   - Ensure LangSmith package is installed

2. **No Traces Appearing**
   - Check network connectivity
   - Verify project name matches
   - Check API endpoint configuration

3. **Performance Issues**
   - Monitor execution times in dashboard
   - Identify slow nodes
   - Check resource usage

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Advanced Features

### Custom Metrics

Add business-specific metrics:

```python
langsmith_monitor.trace_card_recommendation(
    run_tree,
    card_name="Chase Sapphire Preferred",
    score=0.85,
    reasoning="High travel rewards, good annual fee",
    metadata={"user_segment": "frequent_traveler"}
)
```

### Batch Processing

Monitor multiple workflows:

```python
async def process_batch(queries):
    results = []
    for query in queries:
        result = await monitor_workflow_execution(
            user_input=query,
            workflow_func=graph.ainvoke,
            create_initial_state(query)
        )
        results.append(result)
    return results
```

### Integration with Other Tools

- **Grafana**: Create custom dashboards
- **Slack**: Send alerts and notifications
- **Datadog**: Integrate with existing monitoring
- **Custom APIs**: Build your own analytics

## 🎯 Best Practices

1. **Consistent Naming**: Use descriptive names for nodes and operations
2. **Metadata**: Add relevant business context to traces
3. **Error Handling**: Always trace errors for debugging
4. **Performance Monitoring**: Set up alerts for performance degradation
5. **Regular Review**: Analyze traces weekly for optimization opportunities

## 📞 Support

- **LangSmith Docs**: [https://docs.smith.langchain.com/](https://docs.smith.langchain.com/)
- **Community**: [https://github.com/langchain-ai/langsmith](https://github.com/langchain-ai/langsmith)
- **Issues**: Report bugs and feature requests on GitHub

## 🎉 Next Steps

1. **Set up your LangSmith account**
2. **Configure environment variables**
3. **Run the demo script**
4. **Explore the dashboard**
5. **Set up alerts and monitoring**
6. **Optimize based on insights**

Happy monitoring! 🚀

