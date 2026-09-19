"""
IntentCart - Master API Service
API Service: api/main.py

Objective (Phase 22 + Phase L12):
FastAPI microservice exposing:
1. POST /api/discover: Full LLM Intelligence Layer + Untouched ML Subsystem
   - Multi-model racing intent extraction (Gemini + Groq)
   - Deterministic FAISS vector retrieval & hard-constraint filtering
   - Multi-factor hybrid candidate scoring
   - Grounded conversational stylist explanation
2. POST /search: Pure ML retrieval engine (backward-compatible)
3. GET /health: Service and model health status
"""

import os
import sys
import time
from typing import Any, Optional, List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from retrieval.pipeline import IntentCartPipeline
from run_ml_pipeline import parse_query_intent_rule_based
from llm.intent_extractor import intent_extractor
from llm.adapter import map_schema_to_pipeline_args
from llm.explainer import grounded_explainer
from llm.router import router

app = FastAPI(
    title="IntentCart Conversational Discovery Engine",
    description="Constraint-Aware Conversational Fashion Discovery (LLM Racing + ML Subsystem)",
    version="2.0.0"
)

# Singleton ML Pipeline
pipeline: Optional[IntentCartPipeline] = None

@app.on_event("startup")
def startup_event():
    global pipeline
    print("Starting up IntentCart Engine...")
    pipeline = IntentCartPipeline()
    print("IntentCart Engine initialized and ready.")

# --- Models for /search (Pure ML) ---

class SearchRequest(BaseModel):
    query: str = Field(..., example="I need a comfortable minimal summer wedding kurta under 5000 with no floral patterns")
    hard_constraints: Optional[dict[str, Any]] = None
    soft_intent: Optional[dict[str, Any]] = None
    top_k: Optional[int] = Field(default=config.FINAL_K, ge=1, le=20)

class ProductResult(BaseModel):
    rank: int
    product_id: str
    title: str
    final_score: float
    score_breakdown: dict[str, float]
    matched_evidence: list[str]
    product_details: dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    retrieved_count: int
    filtered_count: int
    rejected_count: int
    results: list[ProductResult]

# --- Models for /api/discover (LLM + ML) ---

class DiscoverRequest(BaseModel):
    query: str = Field(..., example="I need a wedding-day kurta for my brother's wedding, comfortable and minimal, no floral patterns, formal and breathable for summer.")
    top_k: Optional[int] = Field(default=config.FINAL_K, ge=1, le=10)

class TelemetryData(BaseModel):
    intent_winner_provider: str
    intent_winner_model: str
    intent_latency_ms: float
    explainer_winner_provider: str
    explainer_winner_model: str
    explainer_latency_ms: float
    total_pipeline_latency_ms: float

class DiscoverResponse(BaseModel):
    query: str
    reformulated_query: str
    hard_constraints: Dict[str, Any]
    soft_preferences: Dict[str, Any]
    telemetry: TelemetryData
    retrieved_count: int
    filtered_count: int
    rejected_count: int
    products: List[ProductResult]
    stylist_explanation: str

# --- Endpoints ---

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Health check endpoint confirming index and LLM readiness."""
    if pipeline is None or pipeline.retriever is None:
        raise HTTPException(status_code=503, detail="ML Pipeline not ready")
    active_providers = [f"{p.provider_name}:{p.model_name}" for p in router.get_configured_providers()]
    return {
        "status": "healthy",
        "service": "IntentCart Conversational Discovery Engine",
        "indexed_products": pipeline.retriever.index.ntotal,
        "embedding_model": config.EMBEDDING_MODEL_NAME,
        "active_llm_providers": active_providers
    }

@app.post("/search", response_model=SearchResponse, tags=["Discovery"])
def search_products(req: SearchRequest):
    """Legacy/Pure ML search endpoint without LLM overhead."""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    extracted_hard, extracted_soft = parse_query_intent_rule_based(req.query)
    
    hard_constraints = dict(extracted_hard)
    if req.hard_constraints:
        hard_constraints.update(req.hard_constraints)

    soft_intent = dict(extracted_soft)
    if req.soft_intent:
        soft_intent.update(req.soft_intent)

    try:
        pipeline_output = pipeline.run(
            query=req.query,
            hard_constraints=hard_constraints,
            soft_intent=soft_intent,
            top_k=req.top_k
        )
        return SearchResponse(
            query=pipeline_output["query"],
            retrieved_count=pipeline_output["retrieved_count"],
            filtered_count=pipeline_output["filtered_count"],
            rejected_count=pipeline_output["rejected_count"],
            results=pipeline_output["results"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

@app.post("/api/discover", response_model=DiscoverResponse, tags=["Conversational Discovery"])
async def discover_products_ai(req: DiscoverRequest):
    """
    Full Conversational AI Discovery Endpoint:
    1. Multi-Model Racing Intent Extraction (Gemini / Groq)
    2. Zero-Loss Parameter Adaptation to ML engine
    3. Untouched FAISS Vector Retrieval + Hard Filters + Hybrid Scoring
    4. Grounded Stylist Conversational Explainer
    """
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    start_total = time.perf_counter()

    try:
        # Step 1: Racing Intent Extraction
        schema, intent_meta = await intent_extractor.extract_intent_async(req.query)

        # Step 2: Adapt to ML Pipeline Arguments
        pipeline_kwargs = map_schema_to_pipeline_args(schema)

        # Step 3: Run Deterministic ML Pipeline
        ml_output = pipeline.run(**pipeline_kwargs, top_k=req.top_k)

        # Step 4: Racing Grounded Explanation
        explanation, explainer_meta = await grounded_explainer.explain_recommendations_async(
            user_query=req.query,
            hard_constraints=pipeline_kwargs["hard_constraints"],
            soft_intent=pipeline_kwargs["soft_intent"],
            pipeline_output=ml_output
        )

        total_latency = round((time.perf_counter() - start_total) * 1000, 2)

        telemetry = TelemetryData(
            intent_winner_provider=intent_meta.get("provider", "unknown"),
            intent_winner_model=intent_meta.get("model", "unknown"),
            intent_latency_ms=intent_meta.get("latency_ms", 0.0),
            explainer_winner_provider=explainer_meta.get("provider", "unknown"),
            explainer_winner_model=explainer_meta.get("model", "unknown"),
            explainer_latency_ms=explainer_meta.get("latency_ms", 0.0),
            total_pipeline_latency_ms=total_latency
        )

        return DiscoverResponse(
            query=req.query,
            reformulated_query=schema.search_query,
            hard_constraints=pipeline_kwargs["hard_constraints"],
            soft_preferences=pipeline_kwargs["soft_intent"],
            telemetry=telemetry,
            retrieved_count=ml_output["retrieved_count"],
            filtered_count=ml_output["filtered_count"],
            rejected_count=ml_output["rejected_count"],
            products=ml_output["results"],
            stylist_explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Discovery error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)
