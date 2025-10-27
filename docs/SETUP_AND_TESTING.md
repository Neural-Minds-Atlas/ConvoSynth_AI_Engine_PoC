# ConvoSynth - Setup and Testing Guide

Complete guide for setting up and testing the ConvoSynth RAG-powered presentation generation system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Data Preparation](#data-preparation)
4. [Starting the Server](#starting-the-server)
5. [Testing the API](#testing-the-api)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+**
- **pip** (Python package manager)
- **Git** (for version control)

### Required API Keys

You need the following API keys in your `.env` file:

```env
# Required for RAG system
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (for other features)
GOOGLE_API_KEY=your_google_api_key_here
```

---

## Environment Setup

### Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd C:\Users\Dell\Desktop\convosynth

# Install all required packages
pip install -r requirements.txt

# Install RAG-Anything with all features
pip install 'raganything[all]'
```

### Step 2: Verify Installation

```bash
# Check RAG-Anything installation
python -c "import raganything; print('RAG-Anything installed successfully')"

# Check LightRAG installation
python -c "import lightrag; print('LightRAG installed successfully')"

# Check other dependencies
python -c "import fastapi, uvicorn, anthropic, openai; print('All dependencies OK')"
```

---

## Data Preparation

### Step 3: Ingest Financial Documents

**IMPORTANT:** You must run this step BEFORE starting the server for the first time.

```bash
# Run the ingestion script
python ingest_financial_documents.py
```

**What to expect:**
- The script processes all PDF files in `data/financial_samples/`
- Processing takes approximately **2-3 hours** for 14 documents
- You'll see live progress with success/failure counts
- Total data ingested: ~77 MB (193 files)
- Knowledge graph: 1559 nodes, 3553 edges

**Output example:**
```
[1/14] Processing: becton-dickinson-q3-2025-earnings.pdf
         Size: 2.45 MB ... [OK] 127.3s
         Progress: [1/14] | Success: 1 | Failed: 0 | Elapsed: 127.3s | ETA: 1653s
```

**Storage location:**
- Data is saved to: `data/rag_storage/`
- Keep this directory - it contains your indexed knowledge base

### Step 4: Verify RAG Storage

```bash
# Check that documents were ingested successfully
python check_rag_storage.py
```

**Expected output:**
```
[1/3] Checking storage directory: data\rag_storage
      [OK] Found 193 files in storage

[2/3] Initializing RAG client...
      [OK] RAG client initialized

[3/3] Testing retrieval with a query...
      Query: 'Becton Dickinson revenue'
      [OK] Retrieved 2437 characters

[SUCCESS] RAG IS WORKING!
```

---

## Starting the Server

### Step 5: Start the FastAPI Server

```bash
# Method 1: Using the run script
python run.py

# Method 2: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**What to expect:**
```
2025-10-04 00:00:00 [info] convosynth_starting version=1.0.0
2025-10-04 00:00:05 [info] rag_client_initialized
2025-10-04 00:00:05 [info] workflow_initialized rag_client_provided=True
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Important startup notes:**
- RAG initialization takes **8-10 seconds** (loading 77 MB of data)
- Server will be ready when you see "Application startup complete"
- If RAG fails to initialize, the server still starts but RAG endpoints will return errors

### Step 6: Verify Server is Running

Open your browser and go to:

**http://localhost:8000**

You should see:
```json
{
  "name": "ConvoSynth API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs"
}
```

---

## Testing the API

### Step 7: Run Comprehensive Test Suite

```bash
# Make sure the server is running first!

# Run the complete test suite
python test_api_complete.py
```

**What this tests:**
1. ✓ Root endpoint
2. ✓ Health checks (basic & detailed)
3. ✓ RAG health status
4. ✓ RAG statistics
5. ✓ RAG queries (4 different queries)
6. ✓ Presentation generation (2 presentations)

**Expected test duration:** 2-3 minutes

**Expected output:**
```
==============================================================================
  CONVOSYNTH API COMPREHENSIVE TEST SUITE
  Testing RAG Integration with FastAPI Backend
==============================================================================

Target: http://localhost:8000
Make sure the server is running: python run.py

Press Enter to start tests...

==============================================================================
  TEST 1: Root Endpoint
==============================================================================

[PASS] Root endpoint accessible

==============================================================================
  TEST 5: RAG Query Tests
==============================================================================

[1/4] Revenue Query
      Query: 'What is Becton Dickinson's revenue for Q3 2025?'
      Mode: hybrid
      [OK] Retrieved 1005 characters in 3.21s

      Preview:
        # Becton Dickinson Revenue Performance

        Becton, Dickinson and Company (BD) demonstrated strong revenue growth...

[SUCCESS] All tests passed!
Your ConvoSynth API with RAG is fully operational!
```

### Step 8: Manual API Testing

#### Using the Interactive API Docs

1. Go to **http://localhost:8000/docs**
2. You'll see all available endpoints
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in the parameters
6. Click "Execute"

#### Using curl Commands

**Test RAG Health:**
```bash
curl http://localhost:8000/api/v1/rag/health
```

**Query RAG System:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Becton Dickinson's revenue?\", \"mode\": \"hybrid\"}"
```

**Generate Presentation:**
```bash
curl -X POST http://localhost:8000/api/v1/presentations/generate \
  -H "Content-Type: application/json" \
  -d "{\"user_input\": \"Create Q3 2025 earnings presentation for Becton Dickinson\", \"slide_count\": 8}"
```

#### Using Python requests

```python
import requests

# Query RAG
response = requests.post(
    "http://localhost:8000/api/v1/rag/query",
    json={"query": "What is Becton Dickinson's revenue for Q3 2025?", "mode": "hybrid"}
)
print(response.json())

# Generate presentation
response = requests.post(
    "http://localhost:8000/api/v1/presentations/generate",
    json={
        "user_input": "Create a Q3 2025 earnings presentation",
        "slide_count": 8
    }
)
result = response.json()
print(f"Status: {result['status']}")
print(f"Slides: {result['total_slides']}")
```

---

## API Endpoints Reference

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint - API info |
| `/api/v1/health` | GET | Basic health check |
| `/api/v1/health/detailed` | GET | Detailed health with RAG status |
| `/api/v1/ping` | GET | Simple ping/pong |

### RAG Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rag/health` | GET | RAG system health check |
| `/api/v1/rag/stats` | GET | RAG system statistics |
| `/api/v1/rag/query` | POST | Query RAG for context |

**RAG Query Request:**
```json
{
  "query": "What is Becton Dickinson's revenue?",
  "mode": "hybrid",  // Options: hybrid, local, global, naive
  "top_k": 40        // Optional: number of results
}
```

**RAG Query Response:**
```json
{
  "query": "What is Becton Dickinson's revenue?",
  "mode": "hybrid",
  "context": "# Becton Dickinson Revenue Performance\n\nBecton, Dickinson...",
  "context_length": 2437,
  "sources": [],
  "metadata": {
    "query_mode": "hybrid",
    "top_k": 40
  }
}
```

### Presentations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/presentations/generate` | POST | Generate presentation |
| `/api/v1/presentations/upload-documents` | POST | Upload documents |

**Presentation Request:**
```json
{
  "user_input": "Create Q3 2025 earnings presentation for Becton Dickinson",
  "slide_count": 8,
  "presentation_type": "financial_overview",
  "focus_areas": ["revenue", "growth"],
  "user_preferences": {}
}
```

**Presentation Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "presentation_html": "<html>...</html>",
  "total_slides": 8,
  "processing_time": 45.2,
  "metadata": {
    "total_time": 45.2,
    "rag_queries": 3
  }
}
```

---

## Query Mode Reference

### Hybrid Mode (Recommended)
- **When to use:** General queries requiring both specific details and broad context
- **Example:** "What is Becton Dickinson's revenue for Q3 2025?"
- **How it works:** Combines vector search and knowledge graph traversal

### Local Mode
- **When to use:** Specific, detailed questions about particular topics
- **Example:** "Medical device segment performance breakdown"
- **How it works:** Focuses on specific entities and their immediate relationships

### Global Mode
- **When to use:** High-level summaries and strategic insights
- **Example:** "Key strategic initiatives and business outlook"
- **How it works:** Analyzes overall themes and patterns across the knowledge graph

### Naive Mode
- **When to use:** Simple keyword-based searches
- **Example:** Quick lookups without complex reasoning
- **How it works:** Basic vector similarity search

---

## Troubleshooting

### Issue: Server won't start

**Check:**
1. Is Python 3.11+ installed? `python --version`
2. Are dependencies installed? `pip list | grep fastapi`
3. Is port 8000 available? `netstat -an | findstr :8000`
4. Check for errors in the console output

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Try a different port
uvicorn src.main:app --port 8001
```

### Issue: RAG not initialized

**Symptoms:**
- `/api/v1/rag/health` returns `"status": "not_initialized"`
- RAG queries return 503 errors

**Check:**
1. Did you run `python ingest_financial_documents.py`?
2. Does `data/rag_storage/` directory exist with files?
3. Check server logs for RAG initialization errors

**Solution:**
```bash
# Verify RAG storage
python check_rag_storage.py

# If storage is missing, re-run ingestion
python ingest_financial_documents.py

# Restart the server
python run.py
```

### Issue: RAG queries return empty results

**Symptoms:**
- Queries return very short context (< 100 characters)
- Context is "None" or error messages

**Check:**
1. Is RAG initialized? Check `/api/v1/rag/health`
2. Is the query relevant to your documents?
3. Check server logs for errors

**Solution:**
```bash
# Test with a known-good query
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Becton Dickinson revenue\", \"mode\": \"hybrid\"}"

# If this fails, check RAG storage
python check_rag_storage.py
```

### Issue: Presentation generation fails

**Symptoms:**
- Status is "failed" with error message
- Takes very long then times out

**Check:**
1. Is RAG initialized and working?
2. Are API keys set in `.env`?
3. Check `presentation_html` for error details

**Solution:**
```bash
# Test RAG first
curl http://localhost:8000/api/v1/rag/health

# Check API keys
python -c "from src.config.settings import get_settings; s = get_settings(); print('OpenAI:', bool(s.openai_api_key)); print('Anthropic:', bool(s.anthropic_api_key))"

# Try a simpler presentation
curl -X POST http://localhost:8000/api/v1/presentations/generate \
  -H "Content-Type: application/json" \
  -d "{\"user_input\": \"Simple overview\", \"slide_count\": 5}"
```

### Issue: Slow query performance

**Normal performance:**
- RAG queries: 2-5 seconds
- Presentation generation: 30-60 seconds

**If slower:**
1. First query after startup is always slower (cache warming)
2. Complex queries take longer
3. Check system resources (RAM, CPU)

**Optimization:**
```python
# Use smaller slide counts
{"slide_count": 5}  # Instead of 15

# Use local mode for faster queries
{"mode": "local"}  # Instead of hybrid

# Reduce top_k
{"top_k": 20}  # Instead of 40
```

---

## Performance Benchmarks

### RAG Query Performance

| Query Type | Mode | Avg Time | Context Length |
|------------|------|----------|----------------|
| Simple revenue | hybrid | 3.2s | 1,000-2,000 chars |
| Growth analysis | hybrid | 3.5s | 2,500-3,500 chars |
| Segment details | local | 2.8s | 2,000-3,000 chars |
| Strategic insights | global | 3.8s | 3,500-4,500 chars |

### Presentation Generation

| Slides | Complexity | Avg Time | HTML Size |
|--------|-----------|----------|-----------|
| 5 | Simple | 25-35s | 15-25 KB |
| 8 | Medium | 40-50s | 30-40 KB |
| 12 | Complex | 60-80s | 50-70 KB |

---

## Next Steps

### Once Everything is Working:

1. **Explore the API docs:** http://localhost:8000/docs
2. **Try different queries:** Experiment with various query modes
3. **Generate presentations:** Create presentations with different parameters
4. **Upload your own documents:** Use the `/upload-documents` endpoint
5. **Integrate with your frontend:** Use the API in your web/mobile app

### Advanced Usage:

- **Custom presentations:** Modify focus_areas and user_preferences
- **Batch processing:** Generate multiple presentations
- **Data analysis:** Query RAG for insights
- **Document management:** Upload and process new documents

---

## Support

If you encounter issues not covered in this guide:

1. Check the server logs for detailed error messages
2. Review the test output from `test_api_complete.py`
3. Verify all API keys are correct in `.env`
4. Ensure all dependencies are installed correctly

---

## Quick Reference Card

```bash
# Setup (one-time)
pip install -r requirements.txt
pip install 'raganything[all]'
python ingest_financial_documents.py

# Start server
python run.py

# Run tests
python test_api_complete.py

# Quick health check
curl http://localhost:8000/api/v1/health

# Quick RAG test
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"revenue\", \"mode\": \"hybrid\"}"

# API documentation
open http://localhost:8000/docs
```

---

**Last Updated:** 2025-10-04
**Version:** 1.0.0
**ConvoSynth** - RAG-Powered Financial Presentation Generation
