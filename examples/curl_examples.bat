@echo off
REM cURL examples for ConvoSynth Agents API (Windows)

set BASE_URL=http://localhost:8000/api/v1/agents

echo ==================================================
echo ConvoSynth Agents API - cURL Examples
echo ==================================================
echo.

REM Example 1: Start a new conversation
echo Example 1: Start New Conversation
echo POST %BASE_URL%/conversation
echo.

curl -X POST "%BASE_URL%/conversation" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"I need to create a presentation about Q3 results\"}"

echo.
echo ---
echo.

REM Save session_id for next requests (replace with actual session_id from response)
set SESSION_ID=conv_example123

REM Example 2: Continue conversation
echo Example 2: Continue Conversation
echo POST %BASE_URL%/conversation (with session_id)
echo.

curl -X POST "%BASE_URL%/conversation" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"The audience is our executive team\", \"session_id\": \"%SESSION_ID%\"}"

echo.
echo ---
echo.

REM Example 3: Get session info
echo Example 3: Get Session Info
echo GET %BASE_URL%/conversation/session/%SESSION_ID%
echo.

curl -X GET "%BASE_URL%/conversation/session/%SESSION_ID%"

echo.
echo ---
echo.

REM Example 4: List all sessions
echo Example 4: List All Sessions
echo GET %BASE_URL%/conversation/sessions
echo.

curl -X GET "%BASE_URL%/conversation/sessions"

echo.
echo ---
echo.

REM Example 5: Get agents info
echo Example 5: Get Agents Info
echo GET %BASE_URL%/agents/info
echo.

curl -X GET "%BASE_URL%/agents/info"

echo.
echo ---
echo.

REM Example 6: Generate presentation (full workflow)
echo Example 6: Generate Presentation (Full Workflow)
echo POST %BASE_URL%/generate-presentation
echo Note: This may take 15-30 seconds
echo.

curl -X POST "%BASE_URL%/generate-presentation" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_request\": \"Create a Q3 2024 financial presentation for executives\", \"preferences\": {\"theme\": \"professional\", \"num_slides\": 8}}"

echo.
echo ---
echo.

REM Example 7: Reset session
echo Example 7: Reset Session
echo POST %BASE_URL%/conversation/reset
echo.

curl -X POST "%BASE_URL%/conversation/reset" ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\": \"%SESSION_ID%\"}"

echo.
echo ---
echo.

REM Example 8: Delete session
echo Example 8: Delete Session
echo DELETE %BASE_URL%/conversation/session/%SESSION_ID%
echo.

curl -X DELETE "%BASE_URL%/conversation/session/%SESSION_ID%"

echo.
echo ==================================================
echo Examples Complete
echo ==================================================
echo.
echo Tips:
echo   - View API docs: http://localhost:8000/docs
echo   - Use Python test script: python examples\test_conversation_api.py
