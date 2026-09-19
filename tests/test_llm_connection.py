"""
IntentCart - Phase L4 LLM Verification Test
Script: tests/test_llm_connection.py

Verifies connectivity and racing latency between Gemini and Groq providers.
"""

import sys
import os

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.router import router
import llm.config as config

def test_connectivity():
    print("=" * 60)
    print(" IntentCart - LLM Multi-Model Connection & Latency Test")
    print("=" * 60)
    print(f"Configured Provider Mode: {config.PROVIDER_MODE}")
    
    configured = router.get_configured_providers()
    print(f"Detected Configured Providers: {[f'{p.provider_name}:{p.model_name}' for p in configured]}")

    if not configured:
        print("\n[!] No API keys found in .env file.")
        print("Please create or edit your .env file with at least one key:")
        print("  GEMINI_API_KEY=your_gemini_key_here")
        print("  GROQ_API_KEY=your_groq_key_here")
        return False

    prompt = "Respond with exactly 5 words: Confirming IntentCart LLM layer is active."
    print(f"\nSending test prompt to active models: '{prompt}'")
    print("Racing models concurrently...\n")

    try:
        response_text, meta = router.generate_text(
            prompt=prompt,
            system_instruction="You are IntentCart's intelligence test agent. Keep answers brief.",
            temperature=0.0,
            max_tokens=50
        )

        print("-" * 60)
        print(f"[PASS] Response Received from Winner: {meta.get('provider').upper()} ({meta.get('model')})")
        print(f"Latency: {meta.get('latency_ms')} ms")
        if meta.get("race_winner"):
            print(f"Race Status: Won race out of {meta.get('total_racers')} racing models!")
        print("-" * 60)
        print(f"Output: {response_text.strip()}")
        print("-" * 60)
        return True
    except Exception as e:
        print(f"[FAIL] Error during generation: {e}")
        return False

if __name__ == "__main__":
    success = test_connectivity()
    sys.exit(0 if success else 1)
