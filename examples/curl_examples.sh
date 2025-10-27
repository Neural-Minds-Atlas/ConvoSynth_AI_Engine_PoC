#!/bin/bash
# cURL examples for ConvoSynth Agents API

BASE_URL="http://localhost:8000/api/v1/agents"

echo "=================================================="
echo "ConvoSynth Agents API - cURL Examples"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Example 1: Start a new conversation
echo -e "${GREEN}Example 1: Start New Conversation${NC}"
echo "POST $BASE_URL/conversation"
echo ""

curl -X POST "$BASE_URL/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to create a presentation about Q3 results"
  }' \
  | jq '.'

echo ""
echo "---"
echo ""

# Save session_id for next requests (replace with actual session_id from response)
SESSION_ID="conv_example123"

# Example 2: Continue conversation with session
echo -e "${GREEN}Example 2: Continue Conversation${NC}"
echo "POST $BASE_URL/conversation (with session_id)"
echo ""

curl -X POST "$BASE_URL/conversation" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"The audience is our executive team\",
    \"session_id\": \"$SESSION_ID\"
  }" \
  | jq '.'

echo ""
echo "---"
echo ""

# Example 3: Get session info
echo -e "${GREEN}Example 3: Get Session Info${NC}"
echo "GET $BASE_URL/conversation/session/{session_id}"
echo ""

curl -X GET "$BASE_URL/conversation/session/$SESSION_ID" \
  | jq '.'

echo ""
echo "---"
echo ""

# Example 4: List all sessions
echo -e "${GREEN}Example 4: List All Sessions${NC}"
echo "GET $BASE_URL/conversation/sessions"
echo ""

curl -X GET "$BASE_URL/conversation/sessions" \
  | jq '.'

echo ""
echo "---"
echo ""

# Example 5: Get agents info
echo -e "${GREEN}Example 5: Get Agents Info${NC}"
echo "GET $BASE_URL/agents/info"
echo ""

curl -X GET "$BASE_URL/agents/info" \
  | jq '.'

echo ""
echo "---"
echo ""

# Example 6: Generate presentation (full workflow)
echo -e "${GREEN}Example 6: Generate Presentation (Full Workflow)${NC}"
echo "POST $BASE_URL/generate-presentation"
echo -e "${BLUE}Note: This may take 15-30 seconds${NC}"
echo ""

curl -X POST "$BASE_URL/generate-presentation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Create a Q3 2024 financial presentation for executives",
    "preferences": {
      "theme": "professional",
      "num_slides": 8,
      "color_scheme": "blue"
    }
  }' \
  | jq '.success, .message, .metadata.query_analysis.query_context'

echo ""
echo "---"
echo ""

# Example 7: Reset session
echo -e "${GREEN}Example 7: Reset Session${NC}"
echo "POST $BASE_URL/conversation/reset"
echo ""

curl -X POST "$BASE_URL/conversation/reset" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\"
  }" \
  | jq '.'

echo ""
echo "---"
echo ""

# Example 8: Delete session
echo -e "${GREEN}Example 8: Delete Session${NC}"
echo "DELETE $BASE_URL/conversation/session/{session_id}"
echo ""

curl -X DELETE "$BASE_URL/conversation/session/$SESSION_ID" \
  | jq '.'

echo ""
echo "=================================================="
echo "Examples Complete"
echo "=================================================="
echo ""
echo "Tips:"
echo "  - Install jq for pretty JSON: https://stedolan.github.io/jq/"
echo "  - View API docs: http://localhost:8000/docs"
echo "  - Use Python test script: python examples/test_conversation_api.py"
