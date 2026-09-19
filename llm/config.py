"""
IntentCart - LLM Intelligence Layer
Module: llm/config.py

Objective:
Centralized configuration for LLM providers. Loads environment variables
from .env deterministically without exposing secrets in source code.
Supports multi-model racing across live Google Gemini & Groq endpoints.
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(override=True)

# Gemini Configuration (Live working endpoint: gemini-flash-latest)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

# Groq Configuration (Live working endpoints on Groq LPU)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b").strip()

# Inference Hyperparameters (low temperature for deterministic intent extraction)
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
DEFAULT_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT", "15.0"))


PROVIDER_MODE = os.getenv("LLM_PROVIDER_MODE", "race").strip().lower()
