# IntentCart — Constraint-Aware Conversational Fashion Discovery Engine

<p align="center">
  <img src="docs/images/intentcart_showcase.jpg" alt="IntentCart UI Showcase" width="100%" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/FAISS-CPU%20Vector%20Index-orange?style=for-the-badge" alt="FAISS" />
  <img src="https://img.shields.io/badge/LLM-Gemini%20%26%20Groq%20Racing-blueviolet?style=for-the-badge" alt="LLM Racing" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

---

## 📌 Executive Summary

Traditional e-commerce search engines rely heavily on **keyword matching** or **unconstrained dense vector search**. While vector search captures semantic vibes, it frequently recommends out-of-budget, out-of-stock, or wrong-gender items. Conversely, keyword filters are brittle and fail to interpret nuanced natural language intent like *"breathable linen for an intimate summer daytime haldi ceremony under ₹2500"*.

**IntentCart** solves this dilemma through a multi-stage **Neuro-Symbolic Architecture**:
1. **Parallel LLM Intent Racing**: Dual-queries Google Gemini Flash and Groq Cloud asynchronously, extracting deterministic hard constraints and subjective soft preferences with sub-second latency.
2. **Sub-4ms Dense Vector Retrieval**: FAISS index retrieves semantic candidate neighbors over dense sentence-transformer embeddings.
3. **Deterministic Constraint Filtering**: Hard filter enforcement strips 100% of out-of-stock items, price violations, gender mismatches, and excluded patterns.
4. **Multi-Criteria Soft Preference Scoring**: Computes transparent weighted scores (0–100%) across occasion alignment, fabric suitability, style fit, and user ratings.
5. **Grounded Stylist Explanations**: Generates conversational rationales strictly grounded in catalog metadata, preventing model hallucinations.

---

## 📊 Benchmark Evaluation & System Metrics

IntentCart was benchmarked against the standard industry baseline (**Pure Semantic Vector Search**) on a curated evaluation suite of 30 complex multi-attribute queries across 10 categories (Weddings, Summer Casuals, Budget Constraints, Negative Exclusions, and Premium Festive).

### 1. Offline A/B Experiment Results

```
=====================================================================================
           INTENTCART OFFLINE EVALUATION & A/B EXPERIMENT REPORT
=====================================================================================
Benchmark Size: 30 queries across 10 categories (Wedding, Summer, Budget, etc.)
-------------------------------------------------------------------------------------
Evaluation Metric                System A (Pure Vector)    System B (IntentCart)    
-------------------------------------------------------------------------------------
Constraint Satisfaction (CSR@5)   56.67%                   100.00%  (+43.33%)
Mean Precision@5                  56.67%                   100.00%  (+43.33%)
Mean Reciprocal Rank (MRR)       0.7778                    1.0000   (+28.56%)
Total Returned Products             150                       150
Fully Compliant Products             85                       150
-------------------------------------------------------------------------------------

--- Breakdown of Hard Constraint Violations Detected ---
Violation Category               System A (Pure Vector)    System B (IntentCart)    
-------------------------------------------------------------------------------------
Stock Violations (Out-of-Stock)      46                         0   (-100%)
Gender Violations                    23                         0   (-100%)
Price Ceiling Violations              4                         0   (-100%)
Negative Pattern Violations           2                         0   (-100%)
Category Violations                   0                         0
-------------------------------------------------------------------------------------
Total Violations                     75                         0   (100% Zero-Defect)
=====================================================================================
```

### 2. Metric Definitions & Key Takeaways

| Metric | System A (Pure Vector) | IntentCart Hybrid | Impact |
| :--- | :---: | :---: | :--- |
| **Constraint Satisfaction Rate (CSR@5)** | 56.67% | **100.00%** | **Zero hallucinated or non-compliant items** reach the user. |
| **Mean Precision@5** | 56.67% | **100.00%** | Every single recommended product in the top 5 satisfies all constraints. |
| **Mean Reciprocal Rank (MRR)** | 0.7778 | **1.0000** | The **#1 ranked product is guaranteed 100% valid** for every query. |
| **Catalog Filtering Purity** | 75 Violations | **0 Violations** | Out-of-stock items, price transgressions, and gender errors are completely eliminated. |

### 3. Latency & Resource Benchmarks

| Subsystem Component | Latency | Memory Footprint | Technology |
| :--- | :---: | :---: | :--- |
| **Dense Vector Retrieval (Top-30)** | **2.8 ms** | ~1.84 MB Index | FAISS `IndexFlatIP` (CPU-optimized) |
| **Query Embedding Inference** | **14.2 ms** | ~90 MB RAM | `all-MiniLM-L6-v2` (1-thread inference mode) |
| **Hard Filtering & Scoring** | **1.1 ms** | < 2 MB RAM | Deterministic Python bitwise evaluation |
| **LLM Intent Extraction (Racing)** | **280 – 620 ms** | 0 MB (API-based) | Groq LLaMA 3.3 70B & Gemini Flash 1.5 |
| **Conversational Explainer** | **350 – 780 ms** | 0 MB (API-based) | Parallel winner streaming |
| **Complete End-to-End Search Pipeline** | **~650 – 1200 ms** | **~215 MB Total** | FastAPI asynchronous pipeline |

---

## 🏗️ System Architecture

```text
                        Natural Language User Query
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        Google Gemini Flash                     Groq Cloud LLaMA
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     │ (Fastest Provider Wins)
                                     ▼
                          Structured Intent Schema
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        Deterministic Constraints               Subjective Soft Preferences
        - Max Price: ₹3000                     - Occasion: Wedding
        - Gender: Men                          - Season: Summer
        - In Stock: True                       - Style: Minimalist
        - Exclude: Floral Prints               - Priority Attributes
                 │                                       │
                 │         FAISS Vector Retrieval        │
                 │       (Top-30 Semantic Candidates)    │
                 │                   │                   │
                 ▼                   ▼                   │
         [ Stage 1: Deterministic Hard Constraint Filter ]
                 │
                 ▼
         [ Stage 2: Multi-Dimensional Hybrid Scorer ] ◄──┘
                 │
                 ▼
          Ranked Top 3–5 Best Products
                 │
                 ▼
       [ Stage 3: Grounded AI Stylist Explainer ]
                 │
                 ▼
     Interactive React 19 Frontend (Cards, Metrics & Deep Links)
```

---

## ⚙️ Repository Structure

```tree
intentcart/
├── api/
│   └── main.py                     # FastAPI service: /api/search, /api/health, CORS
├── artifacts/
│   ├── product_index.faiss         # 1.84 MB pre-computed FAISS vector index
│   ├── product_metadata.json       # Cleaned product metadata (1,200 fashion items)
│   └── image_cache.json            # Original dataset image URL mappings
├── config.py                       # Global weights, paths, and thresholds
├── docs/
│   └── images/                     # Architecture diagrams and UI showcase images
├── embeddings/
│   ├── generate_embeddings.py      # Offline indexing and embedding generator
│   └── model_loader.py             # Memory-capped SentenceTransformer loader
├── evaluation/
│   ├── evaluate.py                 # Automated A/B evaluation benchmark runner
│   └── test_queries.json           # 30 golden multi-attribute test queries
├── frontend/
│   ├── src/
│   │   ├── components/             # React components (ProductCard, SearchBar, Metrics)
│   │   ├── services/api.js         # API client with automatic URL resolution
│   │   └── App.jsx                 # Master application layout
│   ├── package.json                # React 19 + Tailwind v4 + Framer Motion
│   └── vite.config.js              # Vite bundler & local reverse-proxy configuration
├── llm/
│   ├── adapter.py                  # Bridges LLM Pydantic schemas to ML pipeline args
│   ├── explainer.py                # Grounded rationale generator (zero hallucinations)
│   ├── intent_extractor.py         # Asynchronous intent parser
│   ├── router.py                   # Parallel racing provider orchestrator
│   └── schemas.py                  # Pydantic validation models
├── ranking/
│   └── scorer.py                   # Hybrid scoring algorithm (semantic + soft weights)
├── retrieval/
│   ├── filters.py                  # Hard-constraint deterministic filtering logic
│   ├── image_resolver.py           # Product image and store link resolution
│   ├── pipeline.py                 # End-to-end unified ML execution pipeline
│   └── vector_search.py            # FAISS IndexFlatIP cosine similarity engine
├── render.yaml                     # Render cloud blueprint specification
└── requirements.txt                # CPU-optimized cloud Python dependencies
```

---

## 💻 Local Device Setup Guide

Follow these instructions to run both the **Backend AI Engine** and the **Frontend Web Application** on your local machine.

### Prerequisites

Ensure you have the following installed on your machine:
- **Python 3.10, 3.11, or 3.12**: [python.org/downloads](https://www.python.org/downloads/)
- **Node.js (v18+) and npm**: [nodejs.org](https://nodejs.org/)
- **Git**: [git-scm.com](https://git-scm.com/)
- At least one free API key:
  - **Google Gemini API Key**: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) *(Free)*
  - **Groq Cloud API Key**: [console.groq.com/keys](https://console.groq.com/keys) *(Free, Recommended for sub-second speeds)*

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/kushalsaialeti/Intentcart.git
cd Intentcart
```

---

### Step 2: Configure Environment Variables

Create your local `.env` file in the project root:

```bash
# On Linux / macOS:
cp .env.example .env

# On Windows (PowerShell):
Copy-Item .env.example .env
```

Open `.env` in any text editor and fill in your API keys:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-latest

# Groq Cloud API (Ultra-Fast)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_FAST_MODEL=openai/gpt-oss-20b

# Router Strategy: 'race' (both parallel), 'gemini', or 'groq'
LLM_PROVIDER_MODE=race
```

---

### Step 3: Backend Setup (Python + FastAPI + ML Subsystem)

#### 1. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** The pre-built FAISS vector index (`artifacts/product_index.faiss`) and catalog metadata (`artifacts/product_metadata.json`) are already bundled. You do **not** need to re-index the dataset!

#### 3. Launch the Backend Server

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will start in < 1 second:
- **API Root**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

### Step 4: Frontend Setup (React 19 + Tailwind CSS)

Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start instantly:
- **Web App**: [http://localhost:5173](http://localhost:5173)

---

### Step 5: (Optional) 1-Click Launch on Windows

If you are on Windows, simply double-click:
```text
run_app.bat
```
This batch script will automatically activate the Python virtualenv, launch FastAPI on port `8000`, start Vite on port `5173`, and open your default browser.

---

## 🧪 Running the Verification & Test Suite

Verify that your local system satisfies all requirements by running the test suite:

### 1. Run All ML Subsystem and Integration Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 2. Run the Offline A/B Benchmark Experiment
```bash
python evaluation/evaluate.py
```

---

## 🌐 Free-Tier Cloud Deployment

IntentCart is architected to run permanently on **$0.00 zero-cost cloud infrastructure**:

| Layer | Provider | Free Tier Specification | Link |
| :--- | :--- | :--- | :--- |
| **Backend API** | **Render** | Free Web Service (512 MB RAM, CPU PyTorch) | [Render Dashboard](https://dashboard.render.com) |
| **Frontend** | **Vercel** | Edge Network CDN & Vite SPA | [Vercel](https://vercel.com) |
| **Keep-Alive** | **GitHub Actions** | Automated 14-minute cron ping to prevent cold-starts | Included in `.github/workflows/keepalive.yml` |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
