"""Test if workflow is accessible via dependencies."""
import sys
sys.path.insert(0, ".")

print("Testing workflow access...")
print("-" * 50)

# Test 1: Import dependencies module
try:
    from src.api.dependencies import get_workflow, _workflow
    print("[OK] Dependencies module imported")
    print(f"     _workflow = {_workflow}")
except Exception as e:
    print(f"[FAIL] Cannot import dependencies: {e}")
    sys.exit(1)

# Test 2: Try to get workflow
try:
    workflow = get_workflow()
    print(f"[OK] get_workflow() returned: {workflow}")
except Exception as e:
    print(f"[FAIL] get_workflow() failed: {e}")
    print("\nThis means workflow hasn't been set yet.")
    print("The server needs to call set_workflow() during startup.")

# Test 3: Check if server is using the new code
import requests
try:
    response = requests.get("http://localhost:8000/api/v1/health")
    if response.status_code == 200:
        print("\n[OK] Server is responding")

        # Try a presentation
        response = requests.post(
            "http://localhost:8000/api/v1/presentations/generate",
            json={"user_input": "test", "slide_count": 5},
            timeout=5
        )

        data = response.json()
        if data["status"] == "failed" and "503" in str(data.get("error", "")):
            print("[FAIL] Server is NOT using new dependencies code")
            print("\nThe server you're running is OLD!")
            print("\nDo this:")
            print("1. Find the terminal with 'python run.py'")
            print("2. Press Ctrl+C to stop it")
            print("3. Start fresh: python run.py")
            print("4. Wait for 'Application startup complete'")
            print("5. Run this test again")
        else:
            print(f"[OK] Server returned: {data['status']}")
            print("[SUCCESS] Workflow is accessible!")

except Exception as e:
    print(f"[ERROR] Server test failed: {e}")

print("-" * 50)
