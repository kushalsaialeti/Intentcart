"""
IntentCart - Phase L12 Verification Test
Script: tests/test_ai_endpoint.py

Verifies the FastAPI service endpoints:
1. GET /health
2. POST /search (Pure ML)
3. POST /api/discover (Conversational AI Discovery Engine)
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from api.main import app, startup_event

# Ensure startup is called for TestClient
startup_event()
client = TestClient(app)

def test_endpoints():
    print("=" * 75)
    print(" IntentCart - FastAPI Microservice Verification Suite")
    print("=" * 75)

    # 1. Health Check
    print("\n[Test 1] Verifying GET /health ...")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    health_data = resp.json()
    print(f"  -> Status: {health_data['status']}")
    print(f"  -> Indexed Products: {health_data['indexed_products']}")
    print(f"  -> Active LLM Providers: {health_data['active_llm_providers']}")
    print("  [OK] /health passed.")

    # 2. Pure ML Search
    print("\n[Test 2] Verifying POST /search (Pure ML Subsystem) ...")
    search_payload = {
        "query": "Men cotton kurta for wedding",
        "top_k": 3
    }
    resp = client.post("/search", json=search_payload)
    assert resp.status_code == 200, f"Search failed: {resp.text}"
    search_data = resp.json()
    assert len(search_data["results"]) == 3
    print(f"  -> Retrieved {search_data['retrieved_count']}, Filtered {search_data['filtered_count']}, Top product: {search_data['results'][0]['title']}")
    print("  [OK] /search passed.")

    # 3. Conversational AI Discovery
    print("\n[Test 3] Verifying POST /api/discover (Full AI Discovery Engine) ...")
    discover_payload = {
        "query": "I need a wedding-day kurta for my brother's wedding, comfortable and minimal, no floral patterns, formal and breathable for summer.",
        "top_k": 3
    }
    resp = client.post("/api/discover", json=discover_payload)
    assert resp.status_code == 200, f"AI discover failed: {resp.text}"
    discover_data = resp.json()

    print(f"  -> Reformulated Query: \"{discover_data['reformulated_query']}\"")
    print(f"  -> Hard Constraints: {discover_data['hard_constraints']}")
    print(f"  -> Intent Model Winner: {discover_data['telemetry']['intent_winner_provider']} ({discover_data['telemetry']['intent_winner_model']}) in {discover_data['telemetry']['intent_latency_ms']} ms")
    print(f"  -> Explainer Model Winner: {discover_data['telemetry']['explainer_winner_provider']} ({discover_data['telemetry']['explainer_winner_model']}) in {discover_data['telemetry']['explainer_latency_ms']} ms")
    print(f"  -> Total Pipeline Latency: {discover_data['telemetry']['total_pipeline_latency_ms']} ms")
    print(f"  -> Products Returned: {len(discover_data['products'])}")
    print(f"  -> Stylist Explanation (sample): {discover_data['stylist_explanation'][:150]}...")

    # Strict hard constraint check on all returned products
    for prod in discover_data["products"]:
        pat = str(prod["product_details"].get("pattern", "")).lower()
        title = prod["title"].lower()
        assert "floral" not in pat, f"Floral pattern found in product: {prod['title']}"
        assert "floral" not in title, f"Floral title found in product: {prod['title']}"

    print("  [OK] /api/discover passed with 100% constraint satisfaction!")

    print("\n" + "=" * 75)
    print("All FastAPI Endpoints Verified Successfully!")
    print("=" * 75)

if __name__ == "__main__":
    test_endpoints()
