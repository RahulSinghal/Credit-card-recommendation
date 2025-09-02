"""
Unit tests for Extractor Node.
Tests cover happy path, edge cases, and errors as specified in the document.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.nodes.extractor import ExtractorNode
from src.models.state import GraphState, Consent, RequestParsed
from src.tools.base import LLMTool, PolicyTool


class MockLLMTool(LLMTool):
    """Mock LLM tool for testing."""
    
    async def nlu_extract(self, text: str, schema: dict) -> dict:
        """Mock NLU extraction."""
        # Simulate successful extraction
        if "travel" in text.lower():
            return {
                "intent": "recommend_card",
                "goals": ["miles", "travel"],
                "constraints": {"annual_fee_max": 200},
                "jurisdiction": "SG",
                "confidence": 0.9
            }
        elif "cashback" in text.lower():
            return {
                "intent": "recommend_card",
                "goals": ["cashback"],
                "constraints": {"annual_fee_max": 100},
                "jurisdiction": "SG",
                "confidence": 0.85
            }
        else:
            return {
                "intent": "recommend_card",
                "goals": ["rewards"],
                "jurisdiction": "SG",
                "confidence": 0.7
            }
    
    async def explainer(self, card_list, request):
        """Mock explanation generation."""
        return "This card offers great rewards for your spending patterns."


class MockPolicyTool(PolicyTool):
    """Mock policy tool for testing."""
    
    async def lint_final(self, recos, policy):
        """Mock policy linting."""
        return Mock(errors=[], warnings=[])


@pytest.fixture
def mock_llm_tool():
    """Create mock LLM tool."""
    return MockLLMTool()


@pytest.fixture
def mock_policy_tool():
    """Create mock policy tool."""
    return MockPolicyTool()


@pytest.fixture
def extractor_node(mock_llm_tool, mock_policy_tool):
    """Create ExtractorNode instance for testing."""
    return ExtractorNode(mock_llm_tool, mock_policy_tool)


@pytest.fixture
def sample_state():
    """Create sample GraphState for testing."""
    return GraphState(
        session={
            "session_id": "test-session-123",
            "user_query": "I want a travel credit card with low annual fee",
            "locale": "en-SG"
        },
        consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
        telemetry={"events": []},
        errors=[]
    )


class TestExtractorNode:
    """Test cases for ExtractorNode."""
    
    @pytest.mark.asyncio
    async def test_successful_extraction_travel(self, extractor_node, sample_state):
        """Test successful extraction of travel card request."""
        # Execute extractor
        result_state = await extractor_node.execute(sample_state)
        
        # Verify request was parsed
        assert result_state.request is not None
        assert result_state.request.intent == "recommend_card"
        assert "miles" in result_state.request.goals
        assert "travel" in result_state.request.goals
        assert result_state.request.constraints["annual_fee_max"] == 200
        assert result_state.request.jurisdiction == "SG"
        
        # Verify telemetry
        assert len(result_state.telemetry["events"]) > 0
        assert result_state.telemetry["events"][0]["name"] == "extractor.ok"
        
        # Verify no errors
        assert len(result_state.errors) == 0
    
    @pytest.mark.asyncio
    async def test_successful_extraction_cashback(self, extractor_node):
        """Test successful extraction of cashback card request."""
        state = GraphState(
            session={
                "session_id": "test-session-456",
                "user_query": "Best cashback card for groceries",
                "locale": "en-SG"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        result_state = await extractor_node.execute(state)
        
        assert result_state.request is not None
        assert result_state.request.intent == "recommend_card"
        assert "cashback" in result_state.request.goals
        assert result_state.request.constraints["annual_fee_max"] == 100
    
    @pytest.mark.asyncio
    async def test_fallback_parsing(self, extractor_node):
        """Test fallback parsing when LLM fails."""
        # Create state with generic query
        state = GraphState(
            session={
                "session_id": "test-session-789",
                "user_query": "I need a credit card",
                "locale": "en-US"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        result_state = await extractor_node.execute(state)
        
        assert result_state.request is not None
        assert result_state.request.intent == "recommend_card"
        assert result_state.request.goals == ["rewards"]
        assert result_state.request.jurisdiction == "US"
    
    @pytest.mark.asyncio
    async def test_consent_based_filtering(self, extractor_node):
        """Test that personalization is filtered based on consent."""
        # Create state with personalization consent = False
        state = GraphState(
            session={
                "session_id": "test-session-consent",
                "user_query": "Travel card with spending patterns",
                "locale": "en-SG"
            },
            consent=Consent(personalization=False, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        result_state = await extractor_node.execute(state)
        
        assert result_state.request is not None
        # Personalization fields should be empty
        assert result_state.request.spend_focus == {}
        assert result_state.request.priority == []
    
    @pytest.mark.asyncio
    async def test_missing_user_query(self, extractor_node):
        """Test error handling when no user query is provided."""
        state = GraphState(
            session={
                "session_id": "test-session-empty",
                "user_query": "",
                "locale": "en-SG"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        with pytest.raises(ValueError, match="No user query provided"):
            await extractor_node.execute(state)
    
    @pytest.mark.asyncio
    async def test_llm_extraction_failure(self, extractor_node):
        """Test handling of LLM extraction failure."""
        # Create a mock LLM tool that raises an exception
        failing_llm_tool = Mock()
        failing_llm_tool.nlu_extract = AsyncMock(side_effect=Exception("LLM service unavailable"))
        
        failing_extractor = ExtractorNode(failing_llm_tool, MockPolicyTool())
        
        state = GraphState(
            session={
                "session_id": "test-session-llm-fail",
                "user_query": "Travel card please",
                "locale": "en-SG"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        # Should not raise exception, should use fallback parsing
        result_state = await failing_extractor.execute(state)
        
        assert result_state.request is not None
        assert result_state.request.intent == "recommend_card"
        # Should have lower confidence due to fallback
        assert result_state.request.goals == ["miles", "travel"]
    
    @pytest.mark.asyncio
    async def test_request_validation_failure(self, extractor_node):
        """Test handling of request validation failure."""
        # Create a mock LLM tool that returns invalid data
        invalid_llm_tool = Mock()
        invalid_llm_tool.nlu_extract = AsyncMock(return_value={
            "intent": "invalid_intent",  # Invalid intent
            "goals": "not_a_list",  # Invalid type
            "jurisdiction": "SG"
        })
        
        invalid_extractor = ExtractorNode(invalid_llm_tool, MockPolicyTool())
        
        state = GraphState(
            session={
                "session_id": "test-session-validation-fail",
                "user_query": "Travel card",
                "locale": "en-SG"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        # Should not raise exception, should return minimal valid request
        result_state = await invalid_extractor.execute(state)
        
        assert result_state.request is not None
        assert result_state.request.intent == "recommend_card"
        assert result_state.request.goals == ["rewards"]  # Default value
    
    @pytest.mark.asyncio
    async def test_telemetry_tracking(self, extractor_node, sample_state):
        """Test that telemetry events are properly tracked."""
        initial_events = len(sample_state.telemetry["events"])
        
        result_state = await extractor_node.execute(sample_state)
        
        # Should have added one telemetry event
        assert len(result_state.telemetry["events"]) == initial_events + 1
        
        # Verify event details
        event = result_state.telemetry["events"][-1]
        assert event["name"] == "extractor.ok"
        assert "confidence" in event["metadata"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, extractor_node):
        """Test that errors are properly captured in state."""
        # Create a mock LLM tool that raises an exception
        error_llm_tool = Mock()
        error_llm_tool.nlu_extract = AsyncMock(side_effect=Exception("Critical error"))
        
        error_extractor = ExtractorNode(error_llm_tool, MockPolicyTool())
        
        state = GraphState(
            session={
                "session_id": "test-session-error",
                "user_query": "Travel card",
                "locale": "en-SG"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
        
        with pytest.raises(Exception):
            await error_extractor.execute(state)
        
        # Verify error was captured in state
        assert len(state.errors) > 0
        assert state.errors[0]["node"] == "extractor"
        assert "Critical error" in state.errors[0]["error"]


class TestExtractorNodeIntegration:
    """Integration tests for ExtractorNode with real-like data."""
    
    @pytest.mark.asyncio
    async def test_complex_query_parsing(self, extractor_node):
        """Test parsing of complex, realistic queries."""
        complex_queries = [
            "I need a credit card for business travel with lounge access and no foreign transaction fees",
            "Looking for a student card with no annual fee and cashback on groceries",
            "Best premium card for high spenders who travel internationally frequently"
        ]
        
        for query in complex_queries:
            state = GraphState(
                session={
                    "session_id": f"test-complex-{hash(query)}",
                    "user_query": query,
                    "locale": "en-SG"
                },
                consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
                telemetry={"events": []},
                errors=[]
            )
            
            result_state = await extractor_node.execute(state)
            
            # Verify basic structure
            assert result_state.request is not None
            assert result_state.request.intent == "recommend_card"
            assert len(result_state.request.goals) > 0
            assert result_state.request.jurisdiction in ["SG", "US"]
            
            # Verify no errors
            assert len(result_state.errors) == 0
    
    @pytest.mark.asyncio
    async def test_locale_handling(self, extractor_node):
        """Test handling of different locales."""
        locales = ["en-SG", "en-US", "en-GB", "en-AU"]
        
        for locale in locales:
            state = GraphState(
                session={
                    "session_id": f"test-locale-{locale}",
                    "user_query": "Travel credit card",
                    "locale": locale
                },
                consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
                telemetry={"events": []},
                errors=[]
            )
            
            result_state = await extractor_node.execute(state)
            
            # Verify jurisdiction is extracted from locale
            expected_jurisdiction = locale.split("-")[-1]
            assert result_state.request.jurisdiction == expected_jurisdiction


if __name__ == "__main__":
    pytest.main([__file__])

