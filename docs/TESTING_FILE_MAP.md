# 🎯 Complete Test Payload System - File Map

## 📁 What I Created For You

```
ConvoSynth_AI_Engine/
│
├── src/api/routes/
│   └── test_outline_edit_payload.py ⭐⭐⭐
│       ├── EDIT_EXAMPLE_MINIMAL (2 KB)
│       ├── EDIT_EXAMPLE_GLOBAL_CONCISE (85 KB) ✅ FULL DATA
│       ├── EDIT_EXAMPLE_SINGLE_SLIDE (85 KB) ✅ FULL DATA
│       ├── EDIT_EXAMPLE_ADD_DATA (85 KB) ✅ FULL DATA
│       ├── EDIT_EXAMPLE_RESTRUCTURE (85 KB) ✅ FULL DATA
│       └── EDIT_EXAMPLE_CHANGE_VISUALS (85 KB) ✅ FULL DATA
│
├── scripts/
│   └── print_edit_payload.py ⭐⭐
│       └── Helper script to print payloads in JSON format
│
└── docs/
    ├── SWAGGER_TESTING_GUIDE.md ⭐⭐⭐
    │   └── Complete step-by-step testing guide
    ├── QUICK_REFERENCE_TESTING.md ⭐⭐
    │   └── One-page quick reference card
    └── TESTING_FILE_MAP.md ⭐
        └── This file - shows what everything is
```

## 🔄 How The System Works

```
Step 1: Choose Payload
┌─────────────────────────────────────┐
│ test_outline_edit_payload.py        │
│                                     │
│ • EDIT_EXAMPLE_MINIMAL              │
│ • EDIT_EXAMPLE_GLOBAL_CONCISE       │
│ • EDIT_EXAMPLE_SINGLE_SLIDE         │
│ • (and 3 more...)                   │
└─────────────────────────────────────┘
            ↓
Step 2: Print to JSON
┌─────────────────────────────────────┐
│ $ python scripts/print_edit_        │
│   payload.py 1                      │
│                                     │
│ Outputs formatted JSON →            │
└─────────────────────────────────────┘
            ↓
Step 3: Copy to Swagger
┌─────────────────────────────────────┐
│ http://localhost:8000/docs          │
│                                     │
│ POST /api/v1/outline/edit           │
│ [Paste JSON here]                   │
└─────────────────────────────────────┘
            ↓
Step 4: Get Response
┌─────────────────────────────────────┐
│ {                                   │
│   "outlineId": "...",               │
│   "editingMetadata": {              │
│     "isEdited": true,               │
│     "modifiedSlides": [2]           │
│   }                                 │
│ }                                   │
└─────────────────────────────────────┘
```

## 📋 Payload Details

### EDIT_EXAMPLE_MINIMAL (2 KB)

```python
Location: test_outline_edit_payload.py (line ~450)
Size: ~2 KB
Outline: 3 slides (minimal test case)
User Feedback: "Make slide 2 more engaging..."
Target Slide: 2
Query Results: 1 basic query
Best For: Quick validation, first test
```

### EDIT_EXAMPLE_GLOBAL_CONCISE (85 KB) ✅

```python
Location: test_outline_edit_payload.py (line ~30)
Size: ~85 KB
Outline: 10 complete slides (BDX stock analysis)
User Feedback: "Make the entire presentation more concise..."
Target Slide: null (affects all slides)
Query Results: 8 complete queries with full metadata
Includes:
  ✅ 10 slides with all bulletPoints, visualHints, dataMapping
  ✅ 8 queryResults with generatedQuery + llmEnhancedAnswer
  ✅ synthesizedContext with inter_query_insights
  ✅ All extractedInformation fields
  ✅ Performance metrics
Best For: Real-world testing with complete data
```

### Other Full Data Payloads (85 KB each) ✅

```python
EDIT_EXAMPLE_SINGLE_SLIDE
EDIT_EXAMPLE_ADD_DATA
EDIT_EXAMPLE_RESTRUCTURE
EDIT_EXAMPLE_CHANGE_VISUALS

All reuse the same complete previousOutline,
extractedInformation, and queryResults from
EDIT_EXAMPLE_GLOBAL_CONCISE but with different
userFeedback messages.
```

## 🎯 Quick Start Commands

### Print Minimal Example

```bash
python scripts/print_edit_payload.py 1
```

### Print Full BDX Analysis Example

```bash
python scripts/print_edit_payload.py 2
```

### Interactive Mode

```bash
python scripts/print_edit_payload.py
# Then choose 1-6 when prompted
```

### Print All Examples

```bash
python scripts/print_edit_payload.py all
```

## 📚 Documentation Files

### SWAGGER_TESTING_GUIDE.md (MAIN GUIDE)

```
Location: docs/SWAGGER_TESTING_GUIDE.md
Purpose: Complete step-by-step testing guide
Contains:
  • Detailed payload descriptions
  • Step-by-step Swagger UI instructions
  • Troubleshooting section
  • Expected response formats
  • Testing checklist
```

### QUICK_REFERENCE_TESTING.md (CHEAT SHEET)

```
Location: docs/QUICK_REFERENCE_TESTING.md
Purpose: One-page quick reference
Contains:
  • Copy-paste commands
  • Quick troubleshooting
  • Expected response structure
  • Success checklist
```

### TESTING_FILE_MAP.md (THIS FILE)

```
Location: docs/TESTING_FILE_MAP.md
Purpose: Visual map of all files
Contains:
  • File structure diagram
  • Workflow visualization
  • Quick start commands
```

## 🔍 What Makes These Payloads "Complete"?

### ❌ NOT Complete (what you DON'T have in most examples):

```python
"queryResults": [
    # ... (include all query results)  ← Placeholder!
],
"slides": [
    # ... (include all slides)  ← Placeholder!
]
```

### ✅ COMPLETE (what YOU HAVE now):

```python
"queryResults": [
    {
        "queryId": "bdx_sep_2025_metrics",
        "generatedQuery": {
            "query": "What were the opening, high, low...",
            "query_type": "metric",
            "priority": "high",
            "filters": {
                "documents": ["Stock History Becton..."],
                "time_periods": ["Sep 2025"],
                "data_categories": ["financial"],
                "metrics": ["open", "high", "low", "close"]
            },
            "rationale": "Direct extraction of core..."
        },
        "llmEnhancedAnswer": {
            "answer": "BDX stock in September 2025...",
            "confidence": 0.95,
            "extractedData": {
                "metrics": [
                    {
                        "metric_name": "September High",
                        "value": "$193.99",
                        "context": "Reached on September 2, 2025"
                    },
                    # ... 3 more metrics with full data
                ],
                "key_points": [
                    "Price range: $183.73 - $193.99",
                    # ... 4 more key points
                ],
                "sources": [...]
            }
        }
    },
    # ... 7 MORE complete queries like this
],
"slides": [
    {
        "slideNumber": 1,
        "slideType": "title_slide",
        "title": "BDX Stock Performance Analysis",
        "bulletPoints": [
            {
                "bulletText": "August-September 2025...",
                "subBullets": None,
                "requiresData": False,
                "dataMapping": None
            },
            # ... 2 more complete bullets
        ],
        "visualHints": [],
        "speakerNotes": "Welcome slide...",
        "keyMessage": "Deep dive into BDX..."
    },
    # ... 9 MORE complete slides like this
]
```

## 💡 Usage Tips

### For Quick Testing

```bash
python scripts/print_edit_payload.py 1
# → Use MINIMAL for quick validation
```

### For Real-World Testing

```bash
python scripts/print_edit_payload.py 2
# → Use GLOBAL_CONCISE for full BDX analysis
```

### For Specific Scenarios

```bash
python scripts/print_edit_payload.py 3  # Single slide edit
python scripts/print_edit_payload.py 4  # Add more data
python scripts/print_edit_payload.py 5  # Restructure
python scripts/print_edit_payload.py 6  # Change visuals
```

## 🎨 File Sizes

| File                         | Size    | Purpose           |
| ---------------------------- | ------- | ----------------- |
| test_outline_edit_payload.py | ~100 KB | All test payloads |
| print_edit_payload.py        | ~2 KB   | Helper script     |
| SWAGGER_TESTING_GUIDE.md     | ~15 KB  | Main guide        |
| QUICK_REFERENCE_TESTING.md   | ~5 KB   | Quick ref         |
| TESTING_FILE_MAP.md          | ~8 KB   | This file         |

## ✅ What You Can Do Now

1. **Test in Swagger UI** - All payloads ready to copy-paste
2. **Test with Python** - Import and use directly
3. **Test with cURL** - Generate JSON and use curl
4. **Customize** - Modify userFeedback in any payload
5. **Debug** - Full data helps identify issues
6. **Demo** - Show real-world edit functionality

## 🚀 Next Steps

1. Start your server: `python run.py`
2. Print a payload: `python scripts/print_edit_payload.py 1`
3. Open Swagger: http://localhost:8000/docs
4. Test the endpoint with your payload
5. Verify response has `editingMetadata`

---

**Everything you need is ready!** 🎉

No placeholders, no missing data, no manual filling required.
Just run the script, copy, paste, and test!
