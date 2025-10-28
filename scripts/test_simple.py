"""Simple test to verify ConvoSynth is working."""
import requests
import json

print("\n" + "="*60)
print("ConvoSynth Simple Test")
print("="*60)

# Test 1: Health Check
print("\n[Test 1] Health Check...")
try:
    response = requests.get("http://localhost:8000/api/v1/health")
    if response.status_code == 200:
        print("[OK] Server is healthy!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"[FAIL] Server returned status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Cannot connect to server: {e}")
    print("\nIs the server running? Try: python run.py")
    exit(1)

# Test 2: Detailed Health
print("\n[Test 2] Detailed Health Check...")
try:
    response = requests.get("http://localhost:8000/api/v1/health/detailed")
    data = response.json()
    print(f"[OK] API: {data['components']['api']}")
    print(f"[OK] Workflow: {data['components']['workflow']}")
    print(f"[OK] RAG Client: {data['components'].get('rag_client', 'not initialized')}")
    print(f"\nAgents Status:")
    for agent, status in data.get('agents', {}).items():
        print(f"  {agent}: {status}")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 3: Generate Presentation
print("\n[Test 3] Generate Simple Presentation...")
try:
    payload = {
        "user_input": "Create a simple presentation about company overview with key highlights",
        "slide_count": 5
    }

    print(f"Sending request...")
    response = requests.post(
        "http://localhost:8000/api/v1/presentations/generate",
        json=payload,
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\n[OK] Presentation Generated!")
        print(f"  Session ID: {data['session_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Processing Time: {data.get('processing_time', 'N/A')}s")
        print(f"  Total Slides: {data.get('total_slides', 'N/A')}")

        if data.get('error'):
            print(f"  Error: {data['error']}")

        if data.get('presentation_html'):
            html_preview = data['presentation_html'][:200]
            print(f"  HTML Preview: {html_preview}...")

            # Save to file
            with open('test_output.html', 'w', encoding='utf-8') as f:
                f.write(data['presentation_html'])
            print(f"\n[OK] Presentation saved to: test_output.html")
    else:
        print(f"[FAIL] Server returned status {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
print("\nIf you see errors above:")
print("1. Make sure server is running: python run.py")
print("2. Check http://localhost:8000/docs in browser")
print("3. Check .env file has ANTHROPIC_API_KEY and OPENAI_API_KEY")
print()
