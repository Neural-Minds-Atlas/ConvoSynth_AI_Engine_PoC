# 🎯 Swagger UI Examples - Quick Guide

## ✅ What Changed

I've added **built-in example payloads** directly to the Swagger UI interface. You no longer need to copy-paste from files!

## 🚀 How To Use Examples in Swagger UI

### Step 1: Open Swagger UI

```
http://localhost:8000/docs
```

### Step 2: Navigate to the Edit Endpoint

- Scroll to **"agents"** section
- Find **POST /api/v1/outline/edit**
- Click to expand

### Step 3: Click "Try it out"

- Click the **"Try it out"** button in the top right

### Step 4: Select an Example 📋

**NEW!** You'll now see a dropdown menu labeled **"Example"** at the top of the request body:

```
┌─────────────────────────────────────┐
│ Example: [Dropdown ▼]              │
│   • minimal_edit                   │
│   • global_concise                 │
│   • single_slide_edit              │
└─────────────────────────────────────┘
```

### Step 5: Choose Your Example

#### Option 1: **minimal_edit** (Quick Test) ⚡

- **Summary:** Minimal Edit Example (Quick Test)
- **Description:** Small 3-slide outline with simple edit request
- **Best for:** Quick validation
- **Size:** ~2 KB

#### Option 2: **global_concise** (Full BDX Data) 📊

- **Summary:** Global Edit - Make Concise (Full BDX Data)
- **Description:** Complete 10-slide BDX stock analysis with all 8 query results
- **Best for:** Real-world testing
- **Size:** ~85 KB

#### Option 3: **single_slide_edit** (Full BDX Data) 🎯

- **Summary:** Single Slide Edit - Add Emphasis (Full BDX Data)
- **Description:** Edit slide 5 to add emphasis on volatility reduction
- **Best for:** Testing targeted slide modifications
- **Size:** ~85 KB

### Step 6: Click Example to Load It

When you click an example from the dropdown, **the entire request body is automatically filled** with complete data!

### Step 7: Execute

- Click the blue **"Execute"** button
- Wait for response
- Review the results

## 📸 Visual Guide

```
Swagger UI Interface:
┌─────────────────────────────────────────────────────────┐
│ POST /api/v1/outline/edit                               │
│ Edit an existing presentation outline based on user...  │
│                                                          │
│ [Try it out]  ← Click here first                        │
├─────────────────────────────────────────────────────────┤
│ Request body                                            │
│                                                          │
│ Example: [minimal_edit ▼]  ← Select example here       │
│                                                          │
│ {                           ← Request body auto-fills   │
│   "sessionId": "test_session",                          │
│   "userId": "test_user",                                │
│   "userFeedback": "Make slide 2 more engaging...",      │
│   "previousOutline": {                                  │
│     ... (complete data loaded automatically)            │
│   }                                                      │
│ }                                                        │
│                                                          │
│ [Execute]  ← Click to test                              │
└─────────────────────────────────────────────────────────┘
```

## 🎨 What's Included in Each Example

### minimal_edit ⚡

```json
{
  "sessionId": "test_session",
  "userId": "test_user",
  "userFeedback": "Make slide 2 more engaging...",
  "targetSlideForEdit": 2,
  "previousOutline": {
    "totalSlides": 3,
    "slides": [
      /* 3 complete slides */
    ]
  },
  "extractedInformation": {
    /* minimal requirements */
  },
  "queryResults": [
    /* 1 basic query */
  ]
}
```

### global_concise 📊 (FULL DATA)

```json
{
  "sessionId": "session_bdx_stock_001",
  "userId": "user_financial_analyst_001",
  "userFeedback": "Make the entire presentation more concise...",
  "targetSlideForEdit": null,
  "previousOutline": {
    "totalSlides": 10,
    "slides": [
      /* ALL 10 slides with complete data */
    ]
  },
  "extractedInformation": {
    /* Complete BDX requirements */
  },
  "queryResults": [
    /* ALL 8 queries with full metadata */
  ],
  "synthesizedContext": {
    /* Complete with inter-query insights */
  },
  "generatedQueries": [
    /* All 8 generated queries */
  ],
  "performanceMetrics": {
    /* Complete metrics */
  }
}
```

### single_slide_edit 🎯 (FULL DATA)

```json
{
  "sessionId": "session_bdx_stock_001",
  "userId": "user_financial_analyst_001",
  "userFeedback": "Slide 5 needs more emphasis...",
  "targetSlideForEdit": 5,
  "previousOutline": {
    /* Same complete 10-slide outline */
  },
  "extractedInformation": {
    /* Same complete data */
  },
  "queryResults": [
    /* Same 8 complete queries */
  ],
  "synthesizedContext": {
    /* Same complete context */
  }
}
```

## ✅ Benefits of Built-in Examples

1. **No Copy-Paste Needed** - Examples load directly in Swagger UI
2. **No Script Required** - Don't need to run `print_edit_payload.py`
3. **Multiple Options** - 3 different examples to choose from
4. **Complete Data** - All examples have full, real data (no placeholders)
5. **Quick Testing** - Start with minimal, move to full data
6. **Always Available** - Examples are part of the API definition

## 🔄 Switching Between Examples

You can switch between examples at any time:

1. Click the **Example dropdown**
2. Select a different example
3. The request body **automatically updates**
4. Click **Execute** to test

**No need to manually edit or copy-paste anything!**

## 🎯 Recommended Testing Flow

```
Step 1: Test with minimal_edit ⚡
  ↓ (Verify endpoint works)

Step 2: Test with global_concise 📊
  ↓ (Test with full BDX data)

Step 3: Test with single_slide_edit 🎯
  ↓ (Test targeted edits)

Step 4: Customize if needed ✏️
  (Edit the loaded example directly in Swagger UI)
```

## 📝 Customizing Examples

After loading an example, you can:

- Edit any field directly in the request body
- Change the `userFeedback` text
- Modify `targetSlideForEdit` value
- Update any other field as needed

The example is just a starting point - feel free to modify!

## 🚨 Troubleshooting

### "Example dropdown not showing"

**Cause:** Examples failed to import  
**Solution:** Check that `test_outline_edit_payload.py` exists and has no errors

```bash
python -c "from src.api.routes.test_outline_edit_payload import EDIT_EXAMPLE_MINIMAL; print('OK')"
```

### "Request body is empty"

**Cause:** Example not loaded  
**Solution:** Click an example from the dropdown first

### "Still need to paste manually"

**Cause:** Using old version or cache  
**Solution:** Restart server and refresh browser

```bash
# Restart server
Ctrl+C
python run.py

# Hard refresh browser
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

## 🎉 Summary

**Before:** Had to copy-paste from files or run scripts  
**After:** Just select an example from the dropdown!

**Examples are now built into Swagger UI:**

- ⚡ **minimal_edit** - Quick test (2 KB)
- 📊 **global_concise** - Full BDX data (85 KB)
- 🎯 **single_slide_edit** - Targeted edit (85 KB)

**No more copy-pasting! Just click and test!** 🚀
