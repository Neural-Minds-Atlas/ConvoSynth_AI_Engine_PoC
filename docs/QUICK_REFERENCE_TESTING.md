# 🚀 Quick Reference - Outline Edit API Testing

## Copy-Paste Commands

### Print Minimal Payload (Quick Test)

```bash
python scripts/print_edit_payload.py 1
```

### Print Full BDX Stock Analysis Payload

```bash
python scripts/print_edit_payload.py 2
```

### Print All Payloads

```bash
python scripts/print_edit_payload.py all
```

---

## Swagger UI Quick Steps

1. **Start Server:** `python run.py`
2. **Open Browser:** http://localhost:8000/docs
3. **Find Endpoint:** POST /api/v1/outline/edit
4. **Click:** "Try it out"
5. **Paste:** Your payload from print_edit_payload.py
6. **Execute:** Click the blue "Execute" button

---

## Available Test Payloads

| #   | Name           | Size  | Use Case                |
| --- | -------------- | ----- | ----------------------- |
| 1   | MINIMAL        | 2 KB  | Quick validation ⚡     |
| 2   | GLOBAL_CONCISE | 85 KB | Make outline concise 📝 |
| 3   | SINGLE_SLIDE   | 85 KB | Edit specific slide 🎯  |
| 4   | ADD_DATA       | 85 KB | Add more metrics 📊     |
| 5   | RESTRUCTURE    | 85 KB | Reorder slides 🔄       |
| 6   | CHANGE_VISUALS | 85 KB | Update charts 📈        |

**Recommendation:** Start with #1 (MINIMAL), then try #2 (GLOBAL_CONCISE)

---

## Direct File Locations

**Test Payloads:**

```
src/api/routes/test_outline_edit_payload.py
```

**Print Script:**

```
scripts/print_edit_payload.py
```

**Documentation:**

```
docs/SWAGGER_TESTING_GUIDE.md
docs/OUTLINE_EDIT_GUIDE.md
```

---

## Quick Troubleshooting

**422 Error:** Missing required field → Use complete payload from file  
**500 Error:** Agent not initialized → Check src/main.py  
**Timeout:** Try MINIMAL payload first  
**No changes:** Check editingMetadata.modifiedSlides in response

---

## Expected Response Structure

```json
{
  "outlineId": "outline_...",
  "presentationOutline": { ... },
  "editingMetadata": {
    "isEdited": true,
    "modifiedSlides": [2, 3],
    "editSummary": "User requested changes applied"
  }
}
```

**Key Field:** `editingMetadata.modifiedSlides` - Shows which slides changed

---

## File Structure Reference

```
ConvoSynth_AI_Engine/
├── src/
│   └── api/
│       └── routes/
│           ├── outline.py                      # Edit endpoint
│           ├── test_outline_edit_payload.py    # ⭐ TEST PAYLOADS HERE
│           └── test_outline_payloads_complete.py
├── scripts/
│   └── print_edit_payload.py                   # ⭐ PRINT HELPER SCRIPT
└── docs/
    ├── SWAGGER_TESTING_GUIDE.md                # ⭐ FULL TESTING GUIDE
    ├── OUTLINE_EDIT_GUIDE.md
    └── OUTLINE_EDIT_IMPLEMENTATION_SUMMARY.md
```

---

## Python Import (Alternative to Swagger)

```python
from src.api.routes.test_outline_edit_payload import EDIT_EXAMPLE_MINIMAL
import requests

response = requests.post(
    "http://localhost:8000/api/v1/outline/edit",
    json=EDIT_EXAMPLE_MINIMAL
)
print(response.json())
```

---

## cURL Command (Alternative to Swagger)

```bash
# First, print payload to file
python scripts/print_edit_payload.py 1 > payload.json

# Then use curl
curl -X POST "http://localhost:8000/api/v1/outline/edit" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

---

## Success Checklist

- [x] Server running on port 8000
- [x] Can access http://localhost:8000/docs
- [x] Payload printed using script
- [x] Pasted into Swagger UI
- [x] Response 200 received
- [x] editingMetadata present in response
- [x] modifiedSlides shows correct slides

---

## Important Notes

✅ **DO:** Start with MINIMAL payload first  
✅ **DO:** Use the print script for perfect JSON formatting  
✅ **DO:** Check server logs if errors occur  
✅ **DO:** Verify editingMetadata in response

❌ **DON'T:** Manually edit payload fields (use complete payloads)  
❌ **DON'T:** Remove required fields to "simplify"  
❌ **DON'T:** Test full payloads first without validating minimal

---

**Need Help?** Check `docs/SWAGGER_TESTING_GUIDE.md` for detailed instructions!
