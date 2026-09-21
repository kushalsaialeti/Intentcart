"""
IntentCart - LLM Intelligence Layer
Module: llm/schemas.py

Pydantic schemas for validated, structured intent extraction.
"""

from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator

class HardConstraintsSchema(BaseModel):
    gender: Optional[str] = Field(
        default=None,
        description="Target gender strictly from ['Men', 'Women', 'Boys', 'Girls'] or null if unspecified"
    )
    gender_specified: bool = Field(
        default=False,
        description="True ONLY if user explicitly specified a gendered term (e.g. 'men', 'women', 'brother', 'sister'). False if unspecified."
    )
    category: Optional[str] = Field(
        default=None,
        description="Target apparel category (e.g., 'Shirt', 'T-Shirt', 'Kurta', 'Jeans', 'Trousers', 'Dress', 'Top') or null"
    )
    canonical_category: Optional[str] = Field(
        default=None,
        description="Canonical category strictly from ['Shirts', 'T-Shirts', 'Kurtas', 'Jeans', 'Trousers', 'Dresses', 'Tops'] or null"
    )

    @field_validator("gender", "category", "canonical_category", mode="before")
    @classmethod
    def coerce_single_str(cls, v: Any) -> Optional[str]:
        if isinstance(v, list):
            return str(v[0]) if v else None
        if v is None:
            return None
        return str(v).strip() or None
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
    negative_constraints: List[str] = Field(
        default_factory=list,
        description="List of all explicit negative exclusions (e.g. ['no floral', 'no stripes'])"
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

    @field_validator("occasion", "season", mode="before")
    @classmethod
    def coerce_opt_str(cls, v: Any) -> Optional[str]:
        if isinstance(v, list):
            return str(v[0]) if v else None
        if v is None:
            return None
        return str(v).strip() or None

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
        default="",
        description="Dense, keyword-rich query string for dense vector embedding retrieval"
    )

    @field_validator("search_query", mode="before")
    @classmethod
    def coerce_search_query(cls, v: Any) -> str:
        if isinstance(v, list):
            return " ".join(str(x) for x in v) if v else ""
        if v is None:
            return ""
        return str(v).strip()
    is_ambiguous: bool = Field(
        default=False,
        description="True if query lacks basic apparel intent (e.g. 'something good')"
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description="Optional single conversational question if query is completely ambiguous"
    )
