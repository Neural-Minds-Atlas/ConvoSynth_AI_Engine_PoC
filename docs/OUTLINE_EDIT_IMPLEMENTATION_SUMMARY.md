# Outline Agent Edit Functionality - Implementation Summary

## ✅ What Was Implemented

### 1. Updated Request Schema (`OutlineEditRequest`)

**New Fields:**

- `previousOutline` (required): The full outline from `/outline/generate`
- `userFeedback` (required): User's edit request message
- `targetSlideForEdit` (optional): Specific slide number or null for global edits

**Preserved Fields:**

- `extractedInformation`: Original presentation requirements
- `queryResults`: Same RAG results from generation
- `synthesizedContext`: Optional context from Query Agent
- `generatedQueries`: Optional query metadata
- `performanceMetrics`: Optional performance data

### 2. Updated Edit Endpoint (`/api/v1/agents/outline/edit`)

**Input:**

```json
{
  "sessionId": "...",
  "userId": "...",
  "previousOutline": {
    /* full outline */
  },
  "userFeedback": "Make slide 5 more concise",
  "targetSlideForEdit": 5, // or null
  "extractedInformation": {
    /* same as generation */
  },
  "queryResults": [
    /* same as generation */
  ]
}
```

**Output:**
Same format as `/outline/generate` with added `editingMetadata`:

```json
{
  "outlineMetadata": {
    "editingMetadata": {
      "modifiedSlides": [5],
      "addedSlides": [],
      "removedSlides": [],
      "structuralChanges": "Slide 5 simplified..."
    }
  }
}
```

### 3. Updated Agent Logic

**Agent (`agent.py`):**

- Modified `_edit_outline()` to extract and pass `userFeedback`
- Builds editing context with user feedback
- Passes all required data to LLM

**Prompts (`prompts.py`):**

- Added `{user_feedback}` field to `OUTLINE_EDITING_PROMPT`
- Emphasized: "CRITICAL: Focus on the user's specific feedback"
- LLM now receives explicit user instructions

### 4. Documentation & Examples

**Created Files:**

1. `test_outline_edit_payload.py` - 8 complete test examples:

   - Global edits (conciseness)
   - Single slide edits
   - Add more data
   - Restructure slides
   - Change visuals
   - Simplify content
   - Fix data mappings
   - Minimal working example

2. `docs/OUTLINE_EDIT_GUIDE.md` - Comprehensive guide:
   - Endpoint details
   - Request/response schemas
   - Common edit scenarios
   - Best practices
   - Integration examples
   - FAQ

---

## 🔄 User Workflow

1. **Generate initial outline:**

   ```
   POST /outline/generate → Get outline
   ```

2. **Review and provide feedback:**

   ```
   User reviews presentationOutline
   Identifies changes needed
   ```

3. **Edit outline:**

   ```
   POST /outline/edit
   - Pass previous outline
   - Provide user feedback
   - Get updated outline
   ```

4. **Iterate or accept:**
   ```
   Repeat step 3 if needed
   Or accept and proceed to content generation
   ```

---

## 📋 Key Features

✅ **Preserves All Input Data:**

- Same `extractedInformation` as generation
- Same `queryResults` as generation
- Same `synthesizedContext` (optional)
- No re-querying or data loss

✅ **Flexible Editing Modes:**

- **Global edits:** `targetSlideForEdit: null`
- **Single slide edits:** `targetSlideForEdit: 5`
- **Multi-slide edits:** Specify in feedback

✅ **User Feedback Driven:**

- Natural language feedback
- Specific, actionable instructions
- Examples: "Make slide 5 more concise", "Add data to slide 3"

✅ **Change Tracking:**

- `modifiedSlides`: Which slides changed
- `addedSlides`: New slides (if any)
- `removedSlides`: Deleted slides (if any)
- `structuralChanges`: Description of changes

✅ **Maintains Quality:**

- 8-10 slide limit enforced
- Data integrity preserved
- Template compliance checked
- Quality checks re-run

---

## 🧪 Testing Examples

### Example 1: Make Slide More Concise

```json
{
  "userFeedback": "Make slide 5 more concise. Reduce to 3 bullet points max.",
  "targetSlideForEdit": 5
}
```

### Example 2: Add More Data

```json
{
  "userFeedback": "Add exact percentage calculations and volume data to slide 4.",
  "targetSlideForEdit": 4
}
```

### Example 3: Global Simplification

```json
{
  "userFeedback": "Simplify language throughout. Remove jargon.",
  "targetSlideForEdit": null
}
```

### Example 4: Restructure

```json
{
  "userFeedback": "Move recommendations (slide 9) to right after slide 5.",
  "targetSlideForEdit": null
}
```

---

## 🚀 How to Use

### Frontend Integration

```javascript
// Step 1: Generate
const generateResponse = await fetch("/api/v1/agents/outline/generate", {
  method: "POST",
  body: JSON.stringify(generatePayload),
});
const outline = await generateResponse.json();

// Step 2: User provides feedback
const userFeedback = getUserFeedback(); // "Make slide 5 shorter"

// Step 3: Edit
const editResponse = await fetch("/api/v1/agents/outline/edit", {
  method: "POST",
  body: JSON.stringify({
    sessionId: outline.sessionId,
    userId: outline.userId,
    userFeedback: userFeedback,
    targetSlideForEdit: 5,
    previousOutline: outline.presentationOutline,
    extractedInformation: originalExtractedInfo,
    queryResults: originalQueryResults,
  }),
});
const updatedOutline = await editResponse.json();

// Show what changed
console.log(
  "Modified slides:",
  updatedOutline.outlineMetadata.editingMetadata.modifiedSlides
);
```

### Python Integration

```python
# Generate initial outline
outline_response = requests.post('/outline/generate', json=payload)
outline = outline_response.json()

# Edit with user feedback
edit_response = requests.post('/outline/edit', json={
    'sessionId': outline['sessionId'],
    'userId': outline['userId'],
    'userFeedback': 'Make slide 5 more concise',
    'targetSlideForEdit': 5,
    'previousOutline': outline['presentationOutline'],
    'extractedInformation': original_extracted_info,
    'queryResults': original_query_results
})
updated = edit_response.json()
```

---

## 📝 Validation

### Required Field Validation

```python
@validator('userFeedback')
def validate_user_feedback(cls, v):
    if not v or not v.strip():
        raise ValueError("userFeedback cannot be empty")
    return v.strip()
```

### Input Validation Checks

- ✅ `userFeedback` cannot be empty
- ✅ `queryResults` cannot be empty
- ✅ `previousOutline` must be valid PresentationOutline
- ✅ `targetSlideForEdit` must be valid slide number (1-10) or null

---

## 🎯 Response Format

**Success Response:**

```json
{
  "success": true,
  "sessionId": "...",
  "userId": "...",
  "outlineId": "new_outline_id",
  "cycleType": "editing",
  "presentationOutline": {
    // Updated outline
  },
  "outlineMetadata": {
    "editingMetadata": {
      "modifiedSlides": [5],
      "addedSlides": [],
      "removedSlides": [],
      "structuralChanges": "..."
    }
  },
  "performanceMetrics": {
    "responseTime": 1.8,
    "agentIterations": 3,
    "toolCallsMade": 3
  }
}
```

---

## 🔍 Key Implementation Details

### Files Modified

1. **`src/api/routes/outline.py`**

   - Updated `OutlineEditRequest` schema
   - Modified `/edit` endpoint logic
   - Added user feedback validation

2. **`src/agents/outline/agent.py`**

   - Updated `_edit_outline()` method
   - Extracts `userFeedback` from editing context
   - Passes to LLM prompt

3. **`src/agents/outline/prompts.py`**
   - Added `{user_feedback}` to `OUTLINE_EDITING_PROMPT`
   - Emphasized user feedback importance
   - Maintains all other functionality

### Files Created

1. **`src/api/routes/test_outline_edit_payload.py`**

   - 8 complete test examples
   - Covers all edit scenarios

2. **`docs/OUTLINE_EDIT_GUIDE.md`**
   - Complete API documentation
   - Integration examples
   - Best practices

---

## ✅ Checklist

- [x] Updated request schema with `previousOutline` and `userFeedback`
- [x] Modified edit endpoint to handle new schema
- [x] Updated agent to extract and use user feedback
- [x] Enhanced prompts with user feedback emphasis
- [x] Created comprehensive test examples
- [x] Wrote complete documentation
- [x] Validated no code errors
- [x] Maintained backward compatibility with generation endpoint

---

## 🚦 Next Steps

1. **Test the endpoint:**

   ```bash
   # Use test payloads from test_outline_edit_payload.py
   curl -X POST http://localhost:8000/api/v1/agents/outline/edit \
     -H "Content-Type: application/json" \
     -d @test_outline_edit_payload.json
   ```

2. **Frontend integration:**

   - Build UI for user feedback input
   - Display outline with edit capability
   - Show change tracking (modified slides)

3. **Iterate:**
   - Allow multiple edit cycles
   - Store edit history
   - Provide undo functionality (use previous outlines)

---

## 📚 Documentation

- **API Guide:** `docs/OUTLINE_EDIT_GUIDE.md`
- **Test Payloads:** `src/api/routes/test_outline_edit_payload.py`
- **Code:** `src/api/routes/outline.py`, `src/agents/outline/agent.py`

Everything is ready to test! 🎉
