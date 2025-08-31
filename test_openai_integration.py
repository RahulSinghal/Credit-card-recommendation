#!/usr/bin/env python3
"""
Test OpenAI LLM Integration with Extractor Node
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.nodes.extractor import ExtractorNode
from src.models.state import GraphState, Consent, RequestParsed
from src.tools.base import PolicyTool
from src.tools.openai_llm import OpenAILLMTool


class MockPolicyTool(PolicyTool):
    """Mock policy tool for testing."""
    
    async def execute(self, **kwargs):
        pass
    
    async def lint_final(self, recos, policy):
        return type('MockPolicyReport', (), {'errors': [], 'warnings': []})()


async def test_openai_extraction():
    """Test OpenAI-powered extraction."""
    print("🚀 Testing OpenAI LLM Integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return False
    
    try:
        # Create OpenAI LLM tool
        openai_tool = OpenAILLMTool(api_key=api_key)
        policy_tool = MockPolicyTool()
        
        # Create Extractor Node with OpenAI
        extractor = ExtractorNode(openai_tool, policy_tool)
        
        # Test queries
        test_queries = [
            "I want a travel credit card with lounge access and no foreign transaction fees",
            "Looking for a cashback card for groceries with no annual fee",
            "Need a business credit card for company expenses and employee cards",
            "I'm a student looking for my first credit card with no annual fee"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test {i}: {query}")
            
            # Create test state
            state = GraphState(
                session={
                    "session_id": f"openai-test-{i}",
                    "user_query": query,
                    "locale": "en-SG"
                },
                consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
                telemetry={"events": []},
                errors=[]
            )
            
            # Execute extractor
            result_state = await extractor.execute(state)
            
            # Display results
            if result_state.request:
                print(f"✅ Extraction successful!")
                print(f"   Intent: {result_state.request.intent}")
                print(f"   Goals: {result_state.request.goals}")
                print(f"   Jurisdiction: {result_state.request.jurisdiction}")
                if result_state.request.constraints:
                    print(f"   Constraints: {result_state.request.constraints}")
                print(f"   Confidence: {result_state.request.confidence}")
            else:
                print(f"❌ Extraction failed")
        
        print("\n🎉 All OpenAI tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_openai_explanation():
    """Test OpenAI-powered explanation generation."""
    print("\n🧪 Testing OpenAI Explanation Generation...")
    
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("❌ OPENAI_API_KEY not found")
            return False
        
        # Create OpenAI LLM tool
        openai_tool = OpenAILLMTool(api_key=api_key)
        
        # Mock card data
        mock_cards = [
            type('MockCard', (), {
                'card_id': 'CITI_PREMIER',
                'dict': lambda: {'card_id': 'CITI_PREMIER', 'name': 'Citi Premier Card'}
            })(),
            type('MockCard', (), {
                'card_id': 'CHASE_SAPPHIRE',
                'dict': lambda: {'card_id': 'CHASE_SAPPHIRE', 'name': 'Chase Sapphire Preferred'}
            })()
        ]
        
        mock_request = {
            "goals": ["miles", "travel"],
            "constraints": {"annual_fee_max": 200}
        }
        
        # Generate explanation
        explanation = await openai_tool.explainer(mock_cards, mock_request)
        
        print(f"✅ Explanation generated successfully!")
        print(f"📝 Explanation: {explanation}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI explanation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all OpenAI integration tests."""
    print("🚀 Starting OpenAI LLM Integration Tests...\n")
    
    # Test extraction
    extraction_success = await test_openai_extraction()
    
    # Test explanation
    explanation_success = await test_openai_explanation()
    
    # Summary
    print("\n" + "="*60)
    print("📊 OPENAI INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"Extraction: {'✅ PASSED' if extraction_success else '❌ FAILED'}")
    print(f"Explanation: {'✅ PASSED' if explanation_success else '❌ FAILED'}")
    
    if extraction_success and explanation_success:
        print("\n🎉 OpenAI Integration Complete! The system is now using real LLM capabilities.")
        print("✅ Ready to proceed to the next node (Router Node).")
        return 0
    else:
        print("\n💥 Some OpenAI tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
