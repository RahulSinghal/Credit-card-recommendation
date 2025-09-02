"""
Base tool definitions for the Credit Card Recommendation Agent.
Based on document section 3.3.6 - Tool Invocation Contracts
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class CatalogFilters(BaseModel):
    """Filters for catalog queries."""
    category: Optional[str] = None
    geo: Optional[str] = None
    min_income_band: Optional[str] = None
    max_annual_fee: Optional[float] = None
    network: Optional[str] = None


class Card(BaseModel):
    """Card information from catalog."""
    card_id: str
    issuer: str
    network: str
    product_code: str
    annual_fee: float
    apr_percent: float
    geo: List[str]
    min_income_band: str
    category: str


class EligibilityResult(BaseModel):
    """Result of eligibility check."""
    ok: bool
    reasons: List[str]


class UserBands(BaseModel):
    """User information in banded format."""
    age_band: str
    income_band: str
    credit_band: str
    geo: str


class PolicyPack(BaseModel):
    """Policy configuration."""
    version: str
    rules_hash: str
    jurisdiction: str


class Provenance(BaseModel):
    """Data provenance information."""
    source: str
    source_id: str
    collected_at: str
    parser_version: str


class PolicyReport(BaseModel):
    """Policy compliance report."""
    errors: List[str]
    warnings: List[str]


class ToolInterface(ABC):
    """Base interface for all tools."""
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass


class CatalogTool(ToolInterface):
    """Tool for catalog operations."""
    
    async def read(self, category: str, filters: CatalogFilters, opts: Optional[Dict[str, Any]] = None) -> List[Card]:
        """Read cards from catalog."""
        # Implementation will be mocked for testing
        pass
    
    async def upsert(self, cards: List[Card], provenance: Provenance) -> Dict[str, List[str]]:
        """Upsert cards to catalog."""
        # Implementation will be mocked for testing
        pass


class EligibilityTool(ToolInterface):
    """Tool for eligibility checking."""
    
    async def check(self, card: Card, user: UserBands, policy: PolicyPack) -> EligibilityResult:
        """Check card eligibility for user."""
        # Implementation will be mocked for testing
        pass


class ScoringTool(ToolInterface):
    """Tool for card scoring."""
    
    async def score(self, card: Card, req: Dict[str, Any], promos: List[Dict[str, Any]]) -> float:
        """Score card suitability (0.0 to 1.0)."""
        # Implementation will be mocked for testing
        pass


class PolicyTool(ToolInterface):
    """Tool for policy compliance."""
    
    async def lint_final(self, recos: Dict[str, Any], policy: PolicyPack) -> PolicyReport:
        """Lint final recommendations for policy compliance."""
        # Implementation will be mocked for testing
        pass


class LLMTool(ToolInterface):
    """Tool for LLM operations."""
    
    async def nlu_extract(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data using LLM."""
        # Implementation will be mocked for testing
        pass
    
    async def explainer(self, card_list: List[Card], request: Dict[str, Any]) -> str:
        """Generate user-friendly explanations."""
        # Implementation will be mocked for testing
        pass


class WebFetchTool(ToolInterface):
    """Tool for web fetching."""
    
    async def fetch_issuer_catalog(self, geo: str, category: str) -> List[Dict[str, Any]]:
        """Fetch issuer catalog from web."""
        # Implementation will be mocked for testing
        pass

