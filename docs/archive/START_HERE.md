# 🚀 START HERE - ConvoSynth Quick Test Guide

**Last Updated**: 2025-10-02
**Status**: Ready to test with RAG

---

## ⚡ Quick Start (3 Steps)

### Step 1: Kill Any Running Servers
```bash
# Press Ctrl+C in any terminal running the server
# Or close those terminal windows
```

### Step 2: Start Fresh Server
```bash
python run.py
```

**Wait for these messages**:
```
INFO: RAGAnything initialized with config:
INFO: Application startup complete.
```

### Step 3: Run Complete Test (In New Terminal)
```bash
python test_rag_complete.py
```

This will test:
- ✅ Server health
- ✅ All 9 agents
- ✅ RAG integration
- ✅ Simple presentation
- ✅ Financial presentation with RAG

---

## 📊 What To Expect

### Test Output:
```
==================================================================
  CONVOSYNTH COMPREHENSIVE TEST SUITE
  Including RAG Integration Testing
==================================================================

TEST 1: Health Check
[OK] Server is healthy!

TEST 2: Detailed Health & Agent Status
[OK] API: operational
[OK] Workflow: operational
[OK] RAG Client: operational

All 9 agents: ready

TEST 3: Financial Documents Check
[OK] Found 27 documents

TEST 4: Simple Presentation Generation
[OK] Presentation Generated in 0.5s
[OK] Saved to: test_simple_output.html

TEST 5: Financial Presentation with RAG
[OK] Presentation Generated in 15-20s
[OK] Saved to: test_financial_output.html
```

---

## 🔍 Troubleshooting

### Issue: "503: Workflow not initialized"

**Cause**: Server has old code cached

**Fix**:
1. Stop server (Ctrl+C)
2. Wait 5 seconds
3. Start again: `python run.py`
4. Wait for "Application startup complete"
5. Run test again

### Issue: "Connection refused"

**Cause**: Server not running

**Fix**:
```bash
python run.py
```

Wait for startup, then test again.

### Issue: Test hangs or times out

**Cause**: First time processing documents through RAG

**Fix**:
- This is NORMAL on first run
- RAG is processing 27 PDFs
- Can take 2-3 minutes first time
- Subsequent requests will be fast

---

## 📁 Files Generated

After testing, you'll have:

1. **test_simple_output.html**
   - Quick test presentation
   - Generated without RAG
   - Should work instantly

2. **test_financial_output.html**
   - Full financial presentation
   - Uses RAG to retrieve from 27 documents
   - Contains real Becton Dickinson Q3 2025 data

---

## 🎯 Testing RAG Precisely

The test script (`test_rag_complete.py`) verifies:

### 1. RAG Initialization
```
[OK] RAG Client: operational
```

### 2. Documents Loaded
```
[OK] Found 27 documents:
  PDF files: 13
  XLSX files: 2
  CSV files: 1
```

### 3. RAG Processing
When you request financial presentation:
- Agents query RAG for Becton Dickinson data
- RAG searches through 27 documents
- Returns relevant financial metrics
- Agents use this to build presentation

### 4. Verification
Check `test_financial_output.html`:
- Should contain actual company names
- Should have real numbers (revenue, earnings)
- Should reference Q3 2025 data
- Should cite sources from PDFs

---

## 🔬 Advanced RAG Testing

### Test 1: Check RAG Storage
```bash
# After first query, check:
ls data/rag_storage/

# You should see:
# - processed/ (processed documents)
# - vector indexes
# - knowledge graph data
```

### Test 2: Query Specific Data
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/presentations/generate",
    json={
        "user_input": "Create presentation focusing on Becton Dickinson revenue growth and operating margins for Q3 2025",
        "slide_count": 6
    }
)

# Check if response contains:
# - Specific revenue numbers
# - Operating margin percentages
# - Q3 2025 timeframe data
```

### Test 3: Multiple Queries
Run test multiple times:
- First time: Slow (RAG processing documents)
- Second time: Fast (RAG using cached embeddings)
- Third time: Faster (agents learning patterns)

---

## 📈 Performance Expectations

### Simple Presentation (No RAG)
- **Time**: 0.5-2 seconds
- **What**: Basic template generation
- **When**: Use for quick tests

### Financial Presentation (With RAG)
- **First Time**: 2-3 minutes (document processing)
- **Subsequent**: 15-20 seconds (target latency)
- **What**: Full 9-agent pipeline + RAG retrieval
- **When**: Real presentations with data

---

## ✅ Success Criteria

Your system is working if:

1. ✅ Server starts without errors
2. ✅ Health check shows all agents ready
3. ✅ RAG client is operational
4. ✅ Simple presentation generates in <2s
5. ✅ Financial presentation generates
6. ✅ HTML files are created
7. ✅ HTML contains actual data (not placeholders)

---

## 🆘 If Still Not Working

### Check These Files:

1. **.env** - Verify API keys:
```bash
cat .env | grep "API_KEY"

# Should show:
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
```

2. **Server Logs** - Look for errors:
```
# In terminal where server is running
# Should NOT see:
# - ImportError
# - ModuleNotFoundError
# - "Workflow not initialized" during startup
```

3. **Test Output** - Check which test fails:
```bash
python test_rag_complete.py

# Note which test shows [FAIL]
# Share that specific error message
```

---

## 💬 Report Issues

If tests fail, share:

1. **Which test failed** (1, 2, 3, 4, or 5)
2. **Error message** (exact text)
3. **Server startup logs** (first 20 lines)
4. **Test output** (full output from test_rag_complete.py)

---

## 🎉 When It Works

You should see:
```
TEST SUMMARY
  [PASS] health
  [PASS] detailed_health
  [PASS] documents
  [PASS] simple_presentation
  [PASS] financial_presentation

Total: 5/5 tests passed

[SUCCESS] All tests passed! ConvoSynth is fully operational.

Generated Files:
  - test_simple_output.html (simple presentation)
  - test_financial_output.html (financial presentation)
```

Open the HTML files in your browser to see the presentations!

---

**Ready to test? Run these commands**:

```bash
# Terminal 1:
python run.py

# Terminal 2 (wait for startup):
python test_rag_complete.py
```

🚀 **Let's make it work!**
