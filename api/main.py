"""
IntentCart - Master API Service
API Service: api/main.py

Objective (Fast-Paced 60-Minute Prototype Architecture):
Thin FastAPI wrapper around the existing untouched AI Engine:
1. POST /api/search: Frontend-friendly endpoint conforming to Master Specification Section 7
2. GET /api/health: Lightweight health verification endpoint
3. POST /api/discover: Full discovery engine with raw schemas
4. POST /search: Pure ML retrieval engine (backward-compatible)
5. CORS enabled for Vite (http://localhost:5173)
"""

import os
import sys
import time
from typing import Any, Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from retrieval.pipeline import IntentCartPipeline
from retrieval.image_resolver import load_cache, extract_clean_id, resolve_single_product
from run_ml_pipeline import parse_query_intent_rule_based
from llm.intent_extractor import intent_extractor
from llm.adapter import map_schema_to_pipeline_args
from llm.explainer import grounded_explainer
from llm.router import router

app = FastAPI(
    title="IntentCart Conversational Discovery Engine",
    description="Constraint-Aware Conversational Fashion Discovery (LLM Racing + ML Subsystem)",
    version="2.1.0"
)

# Configure CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton ML Pipeline
pipeline: Optional[IntentCartPipeline] = None

@app.on_event("startup")
def startup_event():
    global pipeline
    if pipeline is None:
        print("Starting up IntentCart Engine...")
        pipeline = IntentCartPipeline()
        print("IntentCart Engine initialized and ready.")

# --- Models ---

class SearchInput(BaseModel):
    query: str = Field(..., example="I need a minimal black kurta for a summer wedding under 3000")
    top_k: Optional[int] = Field(default=config.FINAL_K, ge=1, le=10)

class PureMLSearchRequest(BaseModel):
    query: str = Field(...)
    hard_constraints: Optional[dict[str, Any]] = None
    soft_intent: Optional[dict[str, Any]] = None
    top_k: Optional[int] = Field(default=config.FINAL_K, ge=1, le=20)

# --- Endpoints ---

@app.get("/api/health", tags=["Monitoring"])
@app.get("/health", tags=["Monitoring"])
def health_check():
    """Health check endpoint confirming service and index readiness."""
    global pipeline
    if pipeline is None:
        pipeline = IntentCartPipeline()

    active_providers = [f"{p.provider_name}:{p.model_name}" for p in router.get_configured_providers()]
    return {
        "status": "ok",
        "service": "IntentCart API",
        "ai_engine": "available",
        "indexed_products": pipeline.retriever.index.ntotal if pipeline.retriever else 0,
        "embedding_model": config.EMBEDDING_MODEL_NAME,
        "active_llm_providers": active_providers
    }

@app.post("/api/search", tags=["Frontend Discovery API"])
async def search_api(req: SearchInput):
    """
    Standard Frontend API conforming to Master Specification Section 7:
    Wraps existing AI Engine, extracts intent, retrieves and filters via ML,
    and returns rich grounded results.
    """
    global pipeline
    if pipeline is None:
        pipeline = IntentCartPipeline()

    if not req.query or not req.query.strip():
        return {
            "success": False,
            "error": "Search query cannot be empty"
        }

    start_total = time.perf_counter()

    try:
        # 1. Existing LLM Racing Intent Extraction
        schema, intent_meta = await intent_extractor.extract_intent_async(req.query)

        # 2. Existing Adapter
        pipeline_kwargs = map_schema_to_pipeline_args(schema)

        # 3. Existing Untouched ML Retrieval Pipeline
        ml_output = pipeline.run(**pipeline_kwargs, top_k=req.top_k)

        # 4. Existing Grounded Conversational Explainer
        explanation, explainer_meta = await grounded_explainer.explain_recommendations_async(
            user_query=req.query,
            hard_constraints=pipeline_kwargs["hard_constraints"],
            soft_intent=pipeline_kwargs["soft_intent"],
            pipeline_output=ml_output
        )

        total_latency = round((time.perf_counter() - start_total) * 1000, 2)

        # Negative preferences compiled from exclusions
        negative_prefs = []
        if schema.hard_constraints.excluded_patterns:
            negative_prefs.extend([f"no {p}" for p in schema.hard_constraints.excluded_patterns])
        if schema.hard_constraints.excluded_materials:
            negative_prefs.extend([f"no {m}" for m in schema.hard_constraints.excluded_materials])
        if schema.hard_constraints.excluded_colors:
            negative_prefs.extend([f"no {c}" for c in schema.hard_constraints.excluded_colors])

        # Normalize results strictly matching Section 7 schema with real Myntra photos and purchase URLs
        image_cache = load_cache()
        formatted_results = []
        for item in ml_output["results"]:
            details = dict(item["product_details"])
            raw_id = item["product_id"]
            clean_id = extract_clean_id(raw_id)
            details["id"] = raw_id
            details["clean_id"] = clean_id
            details["title"] = item["title"]

            # Real Purchase URL on Myntra
            prod_url = f"https://www.myntra.com/{clean_id}"
            details["product_url"] = prod_url

            # Real Original Dataset Image from Myntra
            cached_entry = image_cache.get(clean_id)
            if cached_entry and cached_entry.get("image_url"):
                details["image_url"] = cached_entry["image_url"]
            elif not details.get("image_url") or details.get("image_url") == "unknown" or str(details.get("image_url")).endswith(f"{clean_id}.jpg"):
                # Dynamically resolve real photo via product ID
                _, real_img, _ = resolve_single_product(clean_id)
                if real_img:
                    details["image_url"] = real_img
                    image_cache[clean_id] = {"image_url": real_img, "product_url": prod_url}

            formatted_results.append({
                "rank": item["rank"],
                "product": details,
                "score": round(item["final_score"], 1),
                "score_breakdown": item["score_breakdown"],
                "matched_requirements": item["matched_evidence"],
                "partial_matches": [],
                "explanation": f"Ranked #{item['rank']} with {round(item['final_score'], 1)}% intent alignment."
            })

        return {
            "success": True,
            "query": req.query,
            "reformulated_query": schema.search_query,
            "intent": {
                "hard_constraints": pipeline_kwargs["hard_constraints"],
                "soft_preferences": pipeline_kwargs["soft_intent"],
                "negative_preferences": negative_prefs
            },
            "results": formatted_results,
            "metadata": {
                "retrieved_count": ml_output["retrieved_count"],
                "filtered_count": ml_output["filtered_count"],
                "rejected_count": ml_output["rejected_count"],
                "final_count": len(formatted_results),
                "telemetry": {
                    "intent_winner": f"{intent_meta.get('provider')} ({intent_meta.get('model')})",
                    "intent_latency_ms": intent_meta.get("latency_ms", 0.0),
                    "explainer_winner": f"{explainer_meta.get('provider')} ({explainer_meta.get('model')})",
                    "explainer_latency_ms": explainer_meta.get("latency_ms", 0.0),
                    "total_pipeline_latency_ms": total_latency
                }
            },
            "stylist_explanation": explanation
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Search failed: {str(e)}"
        }

# --- Backward-compatible endpoints ---

@app.post("/search", tags=["Discovery"])
def search_products(req: PureMLSearchRequest):
    """Legacy/Pure ML search endpoint without LLM overhead."""
    global pipeline
    if pipeline is None:
        pipeline = IntentCartPipeline()

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
        return {
            "query": pipeline_output["query"],
            "retrieved_count": pipeline_output["retrieved_count"],
            "filtered_count": pipeline_output["filtered_count"],
            "rejected_count": pipeline_output["rejected_count"],
            "results": pipeline_output["results"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

@app.post("/api/discover", tags=["Conversational Discovery"])
async def discover_products_ai(req: SearchInput):
    """Alias for /api/search."""
    return await search_api(req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)
