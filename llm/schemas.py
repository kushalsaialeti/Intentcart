"""
IntentCart - LLM Intelligence Layer
Module: llm/schemas.py


"""

from typing import List, Optional
from pydantic import BaseModel, Field

class HardConstraintsSchema(BaseModel):
    gender: Optional[str] = Field(
        default=None,
        description="Target gender strictly from ['Men', 'Women', 'Boys', 'Girls'] or null"
    )
    category: Optional[str] = Field(
        default=None,
        description="Target apparel category (e.g., 'Kurta', 'Shirt', 'Top', 'Jeans', 'Dress') or null"
    )
    max_price: Optional[float] = Field(
        default=None,
        description="Maximum budget in INR (e.g., 5000.0) or null"
    )
    min_price: Optional[float] = Field(
        default=None,
        description="Minimum price in INR or null"
    )
    in_stock_only: bool = Field(
        default=True,
        description="True if out-of-stock items must be rejected"
    )
    excluded_patterns: List[str] = Field(
        default_factory=list,
        description="Patterns strictly excluded by the user (e.g. ['floral', 'striped'])"
    )
    excluded_materials: List[str] = Field(
        default_factory=list,
        description="Materials strictly excluded (e.g. ['polyester', 'synthetic'])"
    )
    excluded_colors: List[str] = Field(
        default_factory=list,
        description="Colors strictly excluded (e.g. ['black', 'red'])"
    )

class SoftPreferencesSchema(BaseModel):
    breathability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance of breathability from 0.0 to 1.0"
    )
    minimalism: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Preference for minimalist/clean design vs loud patterns"
    )
    comfort: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance of soft/comfortable materials"
    )
    formality: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Formality level (0.0 = casual, 1.0 = formal/wedding)"
    )
    occasion: Optional[str] = Field(
        default=None,
        description="Occasion tag: 'wedding', 'festive', 'casual', 'party', 'work', or null"
    )
    season: Optional[str] = Field(
        default=None,
        description="Season tag: 'summer', 'winter', 'monsoon', or null"
    )
    preferred_colors: List[str] = Field(
        default_factory=list,
        description="Colors the user explicitly likes (e.g. ['white', 'navy'])"
    )
    preferred_materials: List[str] = Field(
        default_factory=list,
        description="Materials the user prefers (e.g. ['cotton', 'linen'])"
    )

class ExtractedIntentSchema(BaseModel):
    hard_constraints: HardConstraintsSchema = Field(default_factory=HardConstraintsSchema)
    soft_preferences: SoftPreferencesSchema = Field(default_factory=SoftPreferencesSchema)
    search_query: str = Field(
        description="Dense, keyword-rich query string for dense vector embedding retrieval"
    )
    is_ambiguous: bool = Field(
        default=False,
        description="True if query lacks basic apparel intent (e.g. 'something good')"
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description="Optional single conversational question if query is completely ambiguous"
    )
