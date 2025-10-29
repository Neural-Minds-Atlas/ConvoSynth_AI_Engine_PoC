# Swagger UI Testing Guide - Outline Edit API

## 📋 Overview

This guide shows you how to test the `/outline/edit` endpoint using Swagger UI with pre-filled, complete test payloads.

## 🎯 Quick Start

### Option 1: Using the Python Script (Recommended)

```bash
# Run the helper script to print payloads
python scripts/print_edit_payload.py

# Choose which payload to print (1-6)
# Copy the JSON output
# Paste into Swagger UI
```

### Option 2: Direct Copy from Python File

1. Open `src/api/routes/test_outline_edit_payload.py`
2. Copy one of the complete payload dictionaries
3. Convert to JSON (or use as-is if pasting into Python)
4. Paste into Swagger UI

## 📦 Available Test Payloads

### 1. **EDIT_EXAMPLE_MINIMAL** ⚡ (Recommended for First Test)

- **Size:** ~2 KB
- **Use Case:** Quick validation that the endpoint works
- **User Feedback:** "Make slide 2 more engaging by adding a bullet point about why this analysis matters to investors."
- **Target:** Slide 2
- **Best For:** Initial API testing, debugging

### 2. **EDIT_EXAMPLE_GLOBAL_CONCISE** 📊 (COMPLETE FULL DATA)

- **Size:** ~85 KB
- **Use Case:** Make entire presentation more concise
- **User Feedback:** "Make the entire presentation more concise. Reduce bullet points to 3 per slide maximum and simplify the language."
- **Target:** All slides (targetSlideForEdit = null)
- **Best For:** Testing global edits with complete BDX stock analysis data
- **Contains:**
  - Complete 10-slide outline from generation
  - All 8 query results with full data
  - Complete synthesizedContext with inter-query insights
  - All extractedInformation fields
  - Performance metrics

### 3. **EDIT_EXAMPLE_SINGLE_SLIDE** 🎯 (COMPLETE FULL DATA)

- **Size:** ~85 KB
- **Use Case:** Edit a specific slide with emphasis changes
- **User Feedback:** "Slide 5 needs more emphasis on the volatility reduction. Add a specific calculation showing the percentage change and highlight it as a key achievement."
- **Target:** Slide 5
- **Best For:** Testing targeted slide modifications

### 4. **EDIT_EXAMPLE_ADD_DATA** 📈 (COMPLETE FULL DATA)

- **Size:** ~85 KB
- **Use Case:** Add more specific data points to slides
- **User Feedback:** "Add more specific data points to slides 3 and 4. Include exact percentage changes, average daily volumes, and highlight the highest and lowest trading days with their volumes."
- **Target:** Slides 3 and 4 (targetSlideForEdit = null)
- **Best For:** Testing data enhancement requests

### 5. **EDIT_EXAMPLE_RESTRUCTURE** 🔄 (COMPLETE FULL DATA)

- **Size:** ~85 KB
- **Use Case:** Change slide order/structure
- **User Feedback:** "Move the investment recommendations (slide 9) earlier in the presentation, right after the comparison slide (slide 5). Investors want to see actionable recommendations sooner."
- **Target:** Structural change (targetSlideForEdit = null)
- **Best For:** Testing narrative flow changes

### 6. **EDIT_EXAMPLE_CHANGE_VISUALS** 📊 (COMPLETE FULL DATA)

- **Size:** ~85 KB
- **Use Case:** Modify visualization types
- **User Feedback:** "Replace the line chart on slide 4 with a candlestick chart to better show daily price movements. Also add a volume overlay to show correlation between volume and price volatility."
- **Target:** Slide 4
- **Best For:** Testing visual hint modifications

## 🚀 Step-by-Step Testing in Swagger UI

### 1. Start Your Server

```bash
# From project root
python run.py

# Or if using uvicorn directly
uvicorn src.main:app --reload --port 8000
```

### 2. Open Swagger UI

```
http://localhost:8000/docs
```

### 3. Navigate to Edit Endpoint

- Scroll to **"agents"** section
- Find **POST /api/v1/outline/edit**
- Click **"Try it out"**

### 4. Get Test Payload

**Method A - Use the Script:**

```bash
python scripts/print_edit_payload.py 1
```

This prints `EDIT_EXAMPLE_MINIMAL` to console.

**Method B - Copy from File:**

```python
# Open src/api/routes/test_outline_edit_payload.py
# Copy EDIT_EXAMPLE_MINIMAL
```

### 5. Paste into Swagger UI

- Clear the default request body
- Paste your chosen payload
- Click **"Execute"**

### 6. Review Response

Expected response structure:

```json
{
  "outlineId": "outline_...",
  "sessionId": "test_session",
  "userId": "test_user",
  "presentationOutline": {
    "title": "...",
    "subtitle": "...",
    "totalSlides": 3,
    "narrativeFlow": "...",
    "slides": [...]
  },
  "outlineMetadata": {...},
  "dataIntegration": {...},
  "editingMetadata": {
    "isEdited": true,
    "editTimestamp": "2025-10-29T...",
    "modifiedSlides": [2],
    "editSummary": "User requested changes applied"
  },
  "qualityChecks": {...},
  "performanceMetrics": {...}
}
```

## 🔍 What Each Payload Tests

| Payload            | Tests                              | Expected Behavior                 |
| ------------------ | ---------------------------------- | --------------------------------- |
| **MINIMAL**        | Basic edit functionality           | Adds bullet point to slide 2      |
| **GLOBAL_CONCISE** | Global edits, full data processing | Reduces bullets across all slides |
| **SINGLE_SLIDE**   | Targeted slide modifications       | Enhances slide 5 with emphasis    |
| **ADD_DATA**       | Data enhancement                   | Adds metrics to slides 3-4        |
| **RESTRUCTURE**    | Slide reordering                   | Moves slide 9 to position 6       |
| **CHANGE_VISUALS** | Visual hint updates                | Changes chart types on slide 4    |

## 📊 Complete Data Structure

All **FULL DATA** payloads include:

### ✅ previousOutline (10 slides)

- Title, subtitle, narrative flow
- All 10 slides with complete structure
- All bullet points with dataMapping
- All visual hints with purposes
- Speaker notes and key messages

### ✅ extractedInformation

- Presentation requirements (topic, audience, themes, etc.)
- Data requirements (documents, metrics, time periods, etc.)
- Visual preferences (chart types, style, colors)

### ✅ queryResults (8 complete queries)

Each query includes:

- `queryId`: Unique identifier
- `generatedQuery`: Full query metadata with filters and rationale
- `llmEnhancedAnswer`:
  - Answer text
  - Confidence score
  - Extracted data with metrics
  - Key points
  - Sources

### ✅ synthesizedContext

- Synthesized answers by theme
- Inter-query insights (4 cross-query patterns)
- Data quality notes
- Synthesis metadata

### ✅ generatedQueries

- Full metadata for all 8 queries generated by Query Agent

### ✅ performanceMetrics

- Query generation time
- Retrieval time
- Synthesis time
- Token counts

## 🎨 Customizing Payloads

To create your own test payload:

```python
your_custom_payload = {
    "sessionId": "your_session",
    "userId": "your_user",
    "userFeedback": "Your specific edit request here",
    "targetSlideForEdit": 3,  # or None for global
    "previousOutline": {
        # Copy from EDIT_EXAMPLE_GLOBAL_CONCISE or your own generation
    },
    "extractedInformation": {
        # Copy from EDIT_EXAMPLE_GLOBAL_CONCISE
    },
    "queryResults": [
        # Copy from EDIT_EXAMPLE_GLOBAL_CONCISE
    ],
    "synthesizedContext": {  # Optional but recommended
        # Copy from EDIT_EXAMPLE_GLOBAL_CONCISE
    },
    "generatedQueries": [],  # Optional
    "performanceMetrics": None  # Optional
}
```

## 🐛 Troubleshooting

### Issue: "422 Unprocessable Entity"

**Solution:** Check that all required fields are present:

- `sessionId`
- `userId`
- `previousOutline` (full outline object)
- `userFeedback`
- `extractedInformation`
- `queryResults` (at least one query)

### Issue: "Outline Agent not initialized"

**Solution:** Make sure the agent is initialized at app startup:

```python
# Check src/main.py for agent initialization
from src.api.routes.outline import initialize_outline_agent
initialize_outline_agent()
```

### Issue: Response too slow (>30 seconds)

**Solution:**

- Use `EDIT_EXAMPLE_MINIMAL` first to test basic functionality
- Check Claude API rate limits
- Monitor server logs for LLM call times

### Issue: "Field required" validation errors

**Solution:**

- Use the complete payloads provided (EDIT_EXAMPLE_GLOBAL_CONCISE, etc.)
- Don't manually trim required fields
- Check that nested objects like `bulletPoints` have all required fields

## 📝 Testing Checklist

- [ ] Start server successfully
- [ ] Access Swagger UI at http://localhost:8000/docs
- [ ] Test with EDIT_EXAMPLE_MINIMAL (quick validation)
- [ ] Test with EDIT_EXAMPLE_GLOBAL_CONCISE (full data)
- [ ] Verify editingMetadata in response
- [ ] Check modifiedSlides array matches expected changes
- [ ] Verify response time < 5 seconds for minimal, < 30 seconds for full
- [ ] Test with targetSlideForEdit = null (global edit)
- [ ] Test with targetSlideForEdit = 5 (specific slide)
- [ ] Verify all data mappings preserved in edited outline

## 🎯 Expected Response Times

| Payload Type               | Expected Time |
| -------------------------- | ------------- |
| MINIMAL                    | 2-5 seconds   |
| FULL DATA (specific slide) | 10-20 seconds |
| FULL DATA (global edit)    | 20-40 seconds |

## 📚 Related Documentation

- [Outline Edit API Guide](./OUTLINE_EDIT_GUIDE.md) - Complete API documentation
- [Outline Edit Implementation](./OUTLINE_EDIT_IMPLEMENTATION_SUMMARY.md) - Technical details
- [API Agents Guide](./API_AGENTS_GUIDE.md) - General agent usage

## 💡 Tips

1. **Start Small:** Always test with `EDIT_EXAMPLE_MINIMAL` first
2. **Monitor Logs:** Check server logs for detailed error messages
3. **Use Python Script:** The `print_edit_payload.py` script formats JSON perfectly
4. **Check Response:** Verify `editingMetadata.modifiedSlides` to see what changed
5. **Compare Outputs:** Save generation output and edit output to compare changes

## 🏁 Success Criteria

A successful test should:

- Return HTTP 200
- Include `editingMetadata` with `isEdited: true`
- Show modified slides in `modifiedSlides` array
- Preserve all original data mappings
- Complete within expected time limits
- Return same structure as generation endpoint with added editingMetadata

---

**Ready to test?** Start with:

```bash
python scripts/print_edit_payload.py 1
```

Then paste the output into Swagger UI! 🚀
