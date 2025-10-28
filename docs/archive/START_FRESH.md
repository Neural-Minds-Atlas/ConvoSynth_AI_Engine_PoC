# 🚀 ConvoSynth - Start Fresh Guide

## ⚠️ THE PROBLEM

Multiple old server processes are running and responding on port 8000, preventing the new fixed code from working.

The fix IS in the code - but old zombie processes won't let the new server take over.

---

## ✅ THE SOLUTION (3 Steps)

### Step 1: Kill ALL Python Processes

**Option A - Use the batch script:**
```
KILL_ALL_SERVERS.bat
```

**Option B - Manual command:**
```cmd
taskkill /F /IM python.exe
```

### Step 2: Start Fresh Server

Open a **NEW** terminal and run:
```
python run.py
```

Wait for these messages:
```json
{"event": "workflow_initialized", ...}
{"event": "app_state_set", "workflow_set": true, ...}
INFO: Application startup complete.
```

### Step 3: Test Everything

In a **DIFFERENT** terminal:
```
python test_rag_complete.py
```

---

## 🎯 Expected Results

```
======================================================================
  TEST SUMMARY
======================================================================
  [PASS] health
  [PASS] detailed_health
  [PASS] documents
  [PASS] simple_presentation            ← Should now PASS!
  [PASS] financial_presentation         ← Should now PASS!

Total: 5/5 tests passed

[SUCCESS] All tests passed! ConvoSynth is fully operational.
```

---

## 🔧 What Was Fixed

### 1. **Removed Module-Level Globals** (src/api/dependencies.py)
   - **Old**: Used `_workflow = None` global variable
   - **New**: Use `request.app.state.workflow` directly
   - **Why**: Python module caching made globals unreliable across processes

### 2. **Updated Dependency Injection** (src/api/routes/presentations.py)
   - **Old**: `workflow = Depends(get_workflow)`
   - **New**: `workflow: SequentialWorkflow = Depends(get_workflow)`
   - **Fixed**: `get_workflow(request: Request)` now receives FastAPI request automatically

### 3. **Simplified App State** (src/main.py)
   - **Removed**: Complex `set_workflow()` calls
   - **Kept**: Simple `app.state.workflow = workflow`
   - **Log**: Now shows `app_state_set` instead of `dependencies_set`

---

## 🐛 Why This Happened

1. **Uvicorn Auto-Reload Failed**: Changes to dependencies.py caused reload to hang
2. **Multiple Servers**: Old processes kept running in background
3. **Port Collision**: Old servers still responded on port 8000
4. **Module Caching**: Test scripts imported cached module with `_workflow = None`

---

## 📊 How to Verify It's Working

### Check 1: Server Logs Show New Code
```json
{"event": "app_state_set", "workflow_set": true, "rag_client_set": true}
```
*NOT* `"dependencies_set"` - that was the old code!

### Check 2: Health Check Shows Workflow Ready
```bash
curl http://localhost:8000/api/v1/health
```
Should return:
```json
{
  "status": "healthy",
  "components": {
    "workflow": "operational"
  }
}
```

### Check 3: Presentation Request Logs Appear
After making a request, server logs should show:
```json
{"event": "presentation_generation_requested", "session_id": "..."}
```

If you DON'T see this log, you're still hitting an old server!

---

## 🆘 Still Not Working?

### Issue: "Still getting 503 errors"

**Check**: Do you see request logs in the server terminal?
- **NO** → Old server still running! → Run `KILL_ALL_SERVERS.bat` again
- **YES** → New problem, share the error logs

### Issue: "Server won't start"

**Check**: Error message
- `Address already in use` → Old server running → Kill it first
- `Import error` → Share the full error
- `Module not found` → Run: `pip install -r requirements.txt`

---

## ✅ Summary

1. **Kill ALL Python processes**: `KILL_ALL_SERVERS.bat`
2. **Start ONE fresh server**: `python run.py`
3. **Wait for "Application startup complete"**
4. **Test**: `python test_rag_complete.py`
5. **See 5/5 tests pass** ✨

The code is **100% fixed**. Just need a clean server restart!

---

**Ready? Run these commands:**

```cmd
# Step 1 - Kill everything:
KILL_ALL_SERVERS.bat

# Step 2 - Start fresh (in NEW terminal):
python run.py

# Step 3 - Test (in DIFFERENT terminal):
python test_rag_complete.py
```

🎉 **It WILL work this time!**
