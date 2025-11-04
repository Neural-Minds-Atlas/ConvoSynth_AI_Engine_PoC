Here are 5 test edit queries covering all four classification categories:

## Test Edit Queries

### 1. Visual Edit
```json
{
  "user_request": "Make the title on slide 3 bigger and change the background color to dark blue",
  "session_id": "sess_test_001",
  "presentation_id": "pres_demo_123",
  "user_id": "user_tester_01"
}
```
**Expected Classification**: `visual_edit`  
**Reason**: Only involves HTML/CSS styling changes (font size and color)

---

### 2. Content Edit
```json
{
  "user_request": "Add a new slide about market risks after the financial overview slide and include bullet points about inflation and interest rates",
  "session_id": "sess_test_002",
  "presentation_id": "pres_demo_123",
  "user_id": "user_tester_01"
}
```
**Expected Classification**: `content_edit`  
**Reason**: Requires outline regeneration and new content creation with RAG retrieval

---

### 3. CV Edit (Chart/Visualization Edit)
```json
{
  "user_request": "Update the Q4 revenue chart data to show $5.2M instead of $4.8M and adjust the year-over-year growth percentage accordingly",
  "session_id": "sess_test_003",
  "presentation_id": "pres_demo_123",
  "user_id": "user_tester_01"
}
```
**Expected Classification**: `cv_edit`  
**Reason**: Modifying data displayed in charts/visualizations

---

### 4. Regenerate Entire
```json
{
  "user_request": "Actually, let's start over. I want to create a completely new presentation focused on Q1 results instead of annual summary",
  "session_id": "sess_test_004",
  "presentation_id": "pres_demo_123",
  "user_id": "user_tester_01"
}
```
**Expected Classification**: `regenerate_entire`  
**Reason**: Explicitly requesting full presentation regeneration with different focus

---

### 5. Visual Edit (Another Example)
```json
{
  "user_request": "Center align all the bullet points and increase the spacing between slides",
  "session_id": "sess_test_005",
  "presentation_id": "pres_demo_123",
  "user_id": "user_tester_01"
}
```
**Expected Classification**: `visual_edit`  
**Reason**: Pure CSS/layout changes (alignment and spacing)

---

## Bonus: Edge Case Test

### 6. Ambiguous/Hybrid Request
```json
{
  "user_request": "Make slide 5 look better",
  "session_id": "sess_test_006",
  "presentation_id": "pres_demo_123",
  "user_id": "user_tester_01"
}
```
**Expected Classification**: `content_edit` (fallback to safer option)  
**Reason**: Ambiguous request - agent should default to content_edit for safety

---

You can use these to test:
1. Classification accuracy
2. Modified request quality (how well it structures the vague requests)
3. Response time (should be <1 second)
4. Edge case handling