# 🚀 ConvoSynth - Quick Start Guide

**Get ConvoSynth running in 5 minutes!**

---

## ✅ Prerequisites

1. **Python 3.11+** installed
2. **Claude API Key** (Tier 4 recommended)
3. **Git** (to manage the code)

---

## 📦 Step 1: Install Dependencies

```bash
# Navigate to project
cd C:\Users\Dell\Desktop\convosynth

# Install dependencies
pip install -r requirements.txt
```

**Expected time**: 2-3 minutes

---

## 🔑 Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required:
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Optional (can add later):
# NANO_BANANA_API_KEY=...
# LANGCHAIN_API_KEY=...
```

**On Windows**, use:
```powershell
copy .env.example .env
notepad .env
```

---

## 🧪 Step 3: Test the System

### Option A: Test Individual Agents (Recommended First)
```bash
python test_api.py
```

This will test:
- ✅ Conversation Agent
- ✅ Query Agent
- ⚠️  Workflow (will partially fail without RAG - expected!)

### Option B: Start the API Server
```bash
python run.py
```

The API will be available at:
- 🌐 **API**: http://localhost:8000
- 📚 **Docs**: http://localhost:8000/docs
- ❤️  **Health**: http://localhost:8000/api/v1/health

---

## 🎯 Step 4: Test the API

### Using Browser (Easiest)

1. Open http://localhost:8000/docs
2. Try the `/api/v1/health` endpoint
3. Try `/api/v1/presentations/generate` with sample request:

```json
{
  "user_input": "Generate a Q4 2024 earnings presentation",
  "slide_count": 8,
  "presentation_type": "financial_overview"
}
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Generate presentation
curl -X POST http://localhost:8000/api/v1/presentations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Create Q4 earnings presentation",
    "slide_count": 8
  }'
```

### Using Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())

# Generate presentation
response = requests.post(
    "http://localhost:8000/api/v1/presentations/generate",
    json={
        "user_input": "Generate Q4 earnings presentation",
        "slide_count": 8
    }
)
print(response.json())
```

---

## 📄 Step 5: Add Financial Documents (Optional)

```bash
# Place your PDFs in this folder
C:\Users\Dell\Desktop\convosynth\data\financial_samples\

# Supported formats:
# - PDF (10-K, earnings reports, etc.)
# - DOCX
# - XLSX
# - HTML
```

---

## 🔧 Step 6: Install RAG Dependencies (For Full Functionality)

```bash
pip install lightrag-hku magic-pdf qdrant-client
```

Then start services:

```bash
# Start Docker services (Redis + Qdrant)
docker-compose up -d redis qdrant

# Verify services
docker ps
```

---

## 🎨 Available Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with agent status
- `GET /api/v1/ping` - Simple ping

### Presentations
- `POST /api/v1/presentations/generate` - Generate presentation
- `POST /api/v1/presentations/upload-documents` - Upload PDFs
- `GET /api/v1/presentations/{session_id}` - Retrieve presentation
- `GET /api/v1/presentations/{session_id}/html` - Get HTML output

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
# Make sure you're in the project root
cd C:\Users\Dell\Desktop\convosynth

# Re-install dependencies
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Check .env file exists
ls .env

# Verify key is set
cat .env | grep ANTHROPIC
```

### Issue: "Workflow not initialized"
```bash
# Check logs for startup errors
# The API should initialize workflow on startup
```

### Issue: "RAG client init failed"
This is expected if you haven't installed LightRAG yet. The API will still work for testing agents individually.

---

## 📊 Expected Behavior

### ✅ What Should Work Now
1. **API Server** - Starts successfully
2. **Health Endpoints** - Return status
3. **Individual Agents** - Can be tested via test script
4. **Workflow Orchestration** - Framework is functional

### ⏳ What Needs RAG Integration
1. **Document Processing** - Requires LightRAG + MinerU
2. **Full Workflow** - Needs RAG for context retrieval
3. **Complete Presentations** - Requires end-to-end pipeline

---

## 📈 Next Steps

### For Testing (Current State)
1. ✅ Test individual agents with `test_api.py`
2. ✅ Start API server with `python run.py`
3. ✅ Try health endpoints
4. ✅ Explore API docs at http://localhost:8000/docs

### For Production (Full System)
5. ⏳ Install RAG dependencies
6. ⏳ Start Docker services (Redis + Qdrant)
7. ⏳ Add sample financial documents
8. ⏳ Test complete workflow

---

## 🎯 Quick Command Reference

```bash
# Start API server
python run.py

# Test agents
python test_api.py

# Install RAG (full system)
pip install lightrag-hku magic-pdf qdrant-client

# Start Docker services
docker-compose up -d

# Stop Docker services
docker-compose down

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/api/v1/health
```

---

## 💡 Pro Tips

1. **Start Simple**: Test individual agents first before full workflow
2. **Use Swagger Docs**: http://localhost:8000/docs is your friend
3. **Check Logs**: Watch console output for detailed errors
4. **Incremental Testing**: Add RAG layer by layer

---

## 🆘 Need Help?

1. Check `FINAL_SUMMARY.md` for complete architecture
2. Review `IMPLEMENTATION_STATUS.md` for implementation details
3. Check `SESSION_PROGRESS.md` for development notes

---

## 🎉 You're Ready!

**ConvoSynth is now runnable!** 🚀

Start with: `python run.py`

Then explore: http://localhost:8000/docs
