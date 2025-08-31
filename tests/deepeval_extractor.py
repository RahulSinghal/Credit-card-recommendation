"""
DeepEval tests for Extractor Node.
Tests correctness of parsed JSON vs query as specified in the document.
"""

import pytest
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancy, Faithfulness, ContextRelevancy
from deepeval.test_case import LLMTestCase
from src.nodes.extractor import ExtractorNode
from src.models.state import GraphState, Consent
from src.tools.base import LLMTool, PolicyTool


class MockLLMToolForDeepEval(LLMTool):
    """Mock LLM tool that returns realistic responses for DeepEval testing."""
    
    async def nlu_extract(self, text: str, schema: dict) -> dict:
        """Return structured data based on input text."""
        text_lower = text.lower()
        
        # Travel-related queries
        if any(word in text_lower for word in ["travel", "miles", "airline", "lounge"]):
            return {
                "intent": "recommend_card",
                "goals": ["miles", "travel"],
                "constraints": {"annual_fee_max": 200, "fx_fee_max_pct": 2.5},
                "priority": ["miles", "lounge_access"],
                "spend_focus": {"airlines": 0.6, "hotels": 0.3, "dining": 0.1},
                "jurisdiction": "SG",
                "risk_tolerance": "standard",
                "must_have": ["no_forex_markup", "lounge_access"],
                "nice_to_have": ["metal_card", "concierge_service"],
                "time_horizon": "12m",
                "confidence": 0.92
            }
        
        # Cashback-related queries
        elif any(word in text_lower for word in ["cashback", "cash back", "groceries", "gas"]):
            return {
                "intent": "recommend_card",
                "goals": ["cashback", "rewards"],
                "constraints": {"annual_fee_max": 100, "fx_fee_max_pct": 3.0},
                "priority": ["cashback", "no_annual_fee"],
                "spend_focus": {"groceries": 0.4, "gas": 0.3, "dining": 0.2, "online": 0.1},
                "jurisdiction": "SG",
                "risk_tolerance": "conservative",
                "must_have": ["no_annual_fee", "groceries_cashback"],
                "nice_to_have": ["gas_cashback", "dining_cashback"],
                "time_horizon": "12m",
                "confidence": 0.88
            }
        
        # Student-related queries
        elif any(word in text_lower for word in ["student", "college", "university", "first card"]):
            return {
                "intent": "recommend_card",
                "goals": ["rewards", "building_credit"],
                "constraints": {"annual_fee_max": 0, "min_credit_score": 300},
                "priority": ["no_annual_fee", "credit_building"],
                "spend_focus": {"books": 0.3, "dining": 0.3, "transport": 0.2, "entertainment": 0.2},
                "jurisdiction": "SG",
                "risk_tolerance": "conservative",
                "must_have": ["no_annual_fee", "student_friendly"],
                "nice_to_have": ["rewards_program", "mobile_app"],
                "time_horizon": "24m",
                "confidence": 0.85
            }
        
        # Business-related queries
        elif any(word in text_lower for word in ["business", "corporate", "expenses", "company"]):
            return {
                "intent": "recommend_card",
                "goals": ["business_expenses", "rewards", "reporting"],
                "constraints": {"annual_fee_max": 500, "fx_fee_max_pct": 1.5},
                "priority": ["expense_tracking", "business_rewards", "employee_cards"],
                "spend_focus": {"travel": 0.4, "office_supplies": 0.3, "dining": 0.2, "advertising": 0.1},
                "jurisdiction": "SG",
                "risk_tolerance": "aggressive",
                "must_have": ["expense_reports", "employee_cards", "business_categories"],
                "nice_to_have": ["concierge_service", "travel_insurance"],
                "time_horizon": "12m",
                "confidence": 0.90
            }
        
        # Generic queries
        else:
            return {
                "intent": "recommend_card",
                "goals": ["rewards"],
                "constraints": {"annual_fee_max": 150},
                "priority": ["rewards", "no_annual_fee"],
                "spend_focus": {"general": 1.0},
                "jurisdiction": "SG",
                "risk_tolerance": "standard",
                "must_have": ["rewards_program"],
                "nice_to_have": ["no_annual_fee"],
                "time_horizon": "12m",
                "confidence": 0.75
            }
    
    async def explainer(self, card_list, request):
        """Mock explanation generation."""
        return "This card offers great rewards for your spending patterns."


class MockPolicyToolForDeepEval(PolicyTool):
    """Mock policy tool for DeepEval testing."""
    
    async def lint_final(self, recos, policy):
        """Mock policy linting."""
        return type('MockPolicyReport', (), {'errors': [], 'warnings': []})()


class TestExtractorDeepEval:
    """DeepEval tests for Extractor Node correctness."""
    
    @pytest.fixture
    def extractor_node(self):
        """Create ExtractorNode instance for DeepEval testing."""
        return ExtractorNode(
            MockLLMToolForDeepEval(),
            MockPolicyToolForDeepEval()
        )
    
    @pytest.fixture
    def base_state(self):
        """Create base GraphState for testing."""
        return GraphState(
            session={
                "session_id": "deepeval-test",
                "locale": "en-SG"
            },
            consent=Consent(personalization=True, data_sharing=False, credit_pull="none"),
            telemetry={"events": []},
            errors=[]
        )
    
    @pytest.mark.asyncio
    async def test_travel_query_correctness(self, extractor_node, base_state):
        """Test correctness of travel query parsing."""
        # Test case
        test_case = LLMTestCase(
            input="I need a travel credit card with lounge access and no foreign transaction fees",
            actual_output="",  # Will be filled by extractor
            expected_output="travel card with lounge access and no forex fees",
            context="User wants travel card with specific features"
        )
        
        # Execute extractor
        base_state.session["user_query"] = test_case.input
        result_state = await extractor_node.execute(base_state)
        
        # Update test case with actual output
        test_case.actual_output = str(result_state.request.dict())
        
        # Evaluate correctness
        answer_relevancy = AnswerRelevancy(threshold=0.7)
        faithfulness = Faithfulness(threshold=0.7)
        
        # Check that travel-related goals are extracted
        assert "miles" in result_state.request.goals
        assert "travel" in result_state.request.goals
        assert "lounge_access" in result_state.request.must_have
        assert result_state.request.constraints.get("fx_fee_max_pct", 10) <= 3.0
        
        # Run DeepEval metrics
        answer_score = answer_relevancy.measure(test_case)
        faithfulness_score = faithfulness.measure(test_case)
        
        assert answer_score >= 0.7, f"Answer relevancy too low: {answer_score}"
        assert faithfulness_score >= 0.7, f"Faithfulness too low: {faithfulness_score}"
    
    @pytest.mark.asyncio
    async def test_cashback_query_correctness(self, extractor_node, base_state):
        """Test correctness of cashback query parsing."""
        test_case = LLMTestCase(
            input="Looking for a cashback card for groceries and gas with no annual fee",
            actual_output="",
            expected_output="cashback card for groceries and gas with no annual fee",
            context="User wants cashback card for specific categories"
        )
        
        # Execute extractor
        base_state.session["user_query"] = test_case.input
        result_state = await extractor_node.execute(base_state)
        
        # Update test case
        test_case.actual_output = str(result_state.request.dict())
        
        # Check cashback-specific extraction
        assert "cashback" in result_state.request.goals
        assert result_state.request.constraints.get("annual_fee_max", 1000) <= 100
        assert "groceries" in result_state.request.spend_focus
        assert "gas" in result_state.request.spend_focus
        
        # Evaluate
        answer_relevancy = AnswerRelevancy(threshold=0.7)
        answer_score = answer_relevancy.measure(test_case)
        
        assert answer_score >= 0.7, f"Answer relevancy too low: {answer_score}"
    
    @pytest.mark.asyncio
    async def test_student_query_correctness(self, extractor_node, base_state):
        """Test correctness of student query parsing."""
        test_case = LLMTestCase(
            input="I'm a student looking for my first credit card with no annual fee",
            actual_output="",
            expected_output="student first credit card with no annual fee",
            context="Student wants first credit card"
        )
        
        # Execute extractor
        base_state.session["user_query"] = test_case.input
        result_state = await extractor_node.execute(base_state)
        
        # Update test case
        test_case.actual_output = str(result_state.request.dict())
        
        # Check student-specific extraction
        assert "building_credit" in result_state.request.goals
        assert result_state.request.constraints.get("annual_fee_max", 1000) == 0
        assert "student_friendly" in result_state.request.must_have
        assert result_state.request.risk_tolerance == "conservative"
        
        # Evaluate
        faithfulness = Faithfulness(threshold=0.7)
        faithfulness_score = faithfulness.measure(test_case)
        
        assert faithfulness_score >= 0.7, f"Faithfulness too low: {faithfulness_score}"
    
    @pytest.mark.asyncio
    async def test_business_query_correctness(self, extractor_node, base_state):
        """Test correctness of business query parsing."""
        test_case = LLMTestCase(
            input="Need a business credit card for company expenses and employee cards",
            actual_output="",
            expected_output="business credit card for company expenses and employee cards",
            context="Business owner needs corporate card"
        )
        
        # Execute extractor
        base_state.session["user_query"] = test_case.input
        result_state = await extractor_node.execute(base_state)
        
        # Update test case
        test_case.actual_output = str(result_state.request.dict())
        
        # Check business-specific extraction
        assert "business_expenses" in result_state.request.goals
        assert "expense_reports" in result_state.request.must_have
        assert "employee_cards" in result_state.request.must_have
        assert result_state.request.risk_tolerance == "aggressive"
        
        # Evaluate
        answer_relevancy = AnswerRelevancy(threshold=0.7)
        answer_score = answer_relevancy.measure(test_case)
        
        assert answer_score >= 0.7, f"Answer relevancy too low: {answer_score}"
    
    @pytest.mark.asyncio
    async def test_constraint_extraction_correctness(self, extractor_node, base_state):
        """Test correctness of constraint extraction."""
        test_case = LLMTestCase(
            input="Credit card with annual fee under $100 and no foreign transaction fees",
            actual_output="",
            expected_output="annual fee under $100 and no foreign transaction fees",
            context="User has specific fee constraints"
        )
        
        # Execute extractor
        base_state.session["user_query"] = test_case.input
        result_state = await extractor_node.execute(base_state)
        
        # Update test case
        test_case.actual_output = str(result_state.request.dict())
        
        # Check constraint extraction
        constraints = result_state.request.constraints
        assert constraints.get("annual_fee_max", 1000) <= 100
        assert constraints.get("fx_fee_max_pct", 10) <= 3.0
        
        # Evaluate
        faithfulness = Faithfulness(threshold=0.7)
        faithfulness_score = faithfulness.measure(test_case)
        
        assert faithfulness_score >= 0.7, f"Faithfulness too low: {faithfulness_score}"
    
    @pytest.mark.asyncio
    async def test_consent_respect_correctness(self, extractor_node, base_state):
        """Test that consent is properly respected in extraction."""
        # Test with personalization consent = False
        base_state.consent.personalization = False
        base_state.session["user_query"] = "Travel card with my spending patterns and preferences"
        
        result_state = await extractor_node.execute(base_state)
        
        # Check that personalization fields are empty
        assert result_state.request.spend_focus == {}
        assert result_state.request.priority == []
        
        # But basic extraction should still work
        assert result_state.request.intent == "recommend_card"
        assert "travel" in result_state.request.goals or "miles" in result_state.request.goals
    
    @pytest.mark.asyncio
    async def test_jurisdiction_extraction_correctness(self, extractor_node, base_state):
        """Test correctness of jurisdiction extraction from locale."""
        locales_and_jurisdictions = [
            ("en-SG", "SG"),
            ("en-US", "US"),
            ("en-GB", "GB"),
            ("en-AU", "AU")
        ]
        
        for locale, expected_jurisdiction in locales_and_jurisdictions:
            base_state.session["locale"] = locale
            base_state.session["user_query"] = "Travel credit card"
            
            result_state = await extractor_node.execute(base_state)
            
            assert result_state.request.jurisdiction == expected_jurisdiction, \
                f"Expected {expected_jurisdiction} for locale {locale}, got {result_state.request.jurisdiction}"


if __name__ == "__main__":
    pytest.main([__file__])
