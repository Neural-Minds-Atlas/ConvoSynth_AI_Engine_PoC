"""Complete RAG and Presentation Generation Test."""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Test 1: Basic Health Check"""
    print_section("TEST 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Server is healthy!")
            print(f"  Status: {data['status']}")
            print(f"  Version: {data['version']}")
            return True
        else:
            print(f"[FAIL] Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\nMake sure server is running: python run.py")
        return False

def test_detailed_health():
    """Test 2: Detailed Health with Agents"""
    print_section("TEST 2: Detailed Health & Agent Status")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/detailed", timeout=5)
        data = response.json()

        print(f"[OK] API: {data['components']['api']}")
        print(f"[OK] Workflow: {data['components']['workflow']}")
        print(f"[OK] RAG Client: {data['components'].get('rag_client', 'N/A')}")

        print("\nAgent Status:")
        agents = data.get('agents', {})
        all_ready = True
        for agent_name, agent_status in agents.items():
            status_symbol = "[OK]" if agent_status == "ready" else "[FAIL]"
            print(f"  {status_symbol} {agent_name}: {agent_status}")
            if agent_status != "ready":
                all_ready = False

        return all_ready
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_rag_documents():
    """Test 3: Check RAG Documents"""
    print_section("TEST 3: Financial Documents Check")

    docs_path = Path("data/financial_samples")
    if not docs_path.exists():
        print("[WARN] No financial_samples directory found")
        return False

    pdf_files = list(docs_path.glob("**/*.pdf"))
    xlsx_files = list(docs_path.glob("**/*.xlsx"))
    csv_files = list(docs_path.glob("**/*.csv"))

    total_docs = len(pdf_files) + len(xlsx_files) + len(csv_files)

    print(f"[OK] Found {total_docs} documents:")
    print(f"  PDF files: {len(pdf_files)}")
    print(f"  XLSX files: {len(xlsx_files)}")
    print(f"  CSV files: {len(csv_files)}")

    if pdf_files:
        print(f"\nSample PDF files:")
        for pdf in pdf_files[:5]:
            print(f"  - {pdf.name}")

    return total_docs > 0

def test_simple_presentation():
    """Test 4: Generate Simple Presentation (No RAG)"""
    print_section("TEST 4: Simple Presentation Generation")

    payload = {
        "user_input": "Create a 5-slide presentation about quarterly business overview",
        "slide_count": 5,
        "presentation_type": "business_overview"
    }

    print(f"Request: {payload['user_input']}")
    print(f"Slides: {payload['slide_count']}")
    print("\nSending request...")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/presentations/generate",
            json=payload,
            timeout=120
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            print(f"\n[OK] Presentation Generated in {elapsed:.2f}s")
            print(f"  Session ID: {data['session_id']}")
            print(f"  Status: {data['status']}")

            if data['status'] == 'failed':
                print(f"  [ERROR] {data.get('error', 'Unknown error')}")
                return False

            print(f"  Processing Time: {data.get('processing_time', 'N/A')}s")
            print(f"  Total Slides: {data.get('total_slides', 'N/A')}")

            if data.get('presentation_html'):
                html_len = len(data['presentation_html'])
                print(f"  HTML Length: {html_len} characters")

                # Save output
                output_file = "test_simple_output.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(data['presentation_html'])
                print(f"  [OK] Saved to: {output_file}")

            return data['status'] == 'completed'
        else:
            print(f"[FAIL] Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_financial_presentation():
    """Test 5: Generate Financial Presentation (With RAG)"""
    print_section("TEST 5: Financial Presentation with RAG")

    payload = {
        "user_input": "Create a Q3 2025 earnings presentation for Becton Dickinson with key financial metrics, revenue analysis, and market performance",
        "slide_count": 8,
        "presentation_type": "financial_overview"
    }

    print(f"Request: {payload['user_input']}")
    print(f"Slides: {payload['slide_count']}")
    print(f"Type: {payload['presentation_type']}")
    print("\nThis will use RAG to retrieve financial data...")
    print("Sending request (may take up to 20 seconds)...")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/presentations/generate",
            json=payload,
            timeout=120
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            print(f"\n[OK] Presentation Generated in {elapsed:.2f}s")
            print(f"  Session ID: {data['session_id']}")
            print(f"  Status: {data['status']}")

            if data['status'] == 'failed':
                print(f"  [ERROR] {data.get('error', 'Unknown error')}")
                print("\nThis might be expected if:")
                print("  - Documents haven't been processed by RAG yet")
                print("  - RAG initialization had issues")
                print("  - Agent execution encountered errors")
                return False

            print(f"  Processing Time: {data.get('processing_time', 'N/A')}s")
            print(f"  Total Slides: {data.get('total_slides', 'N/A')}")

            # Check metadata for stage timings
            metadata = data.get('metadata', {})
            if metadata.get('stage_timings'):
                print("\n  Stage Timings:")
                for stage, timing in metadata['stage_timings'].items():
                    print(f"    {stage}: {timing}s")

            if data.get('presentation_html'):
                html_len = len(data['presentation_html'])
                print(f"  HTML Length: {html_len} characters")

                # Save output
                output_file = "test_financial_output.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(data['presentation_html'])
                print(f"  [OK] Saved to: {output_file}")

                # Check if HTML contains financial data
                html = data['presentation_html']
                has_numbers = any(char.isdigit() for char in html)
                print(f"  Contains numbers: {has_numbers}")

            return data['status'] == 'completed'
        else:
            print(f"[FAIL] Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.Timeout:
        print(f"[TIMEOUT] Request took longer than 120 seconds")
        print("The server might still be processing. Check server logs.")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  CONVOSYNTH COMPREHENSIVE TEST SUITE")
    print("  Including RAG Integration Testing")
    print("="*70)

    results = {}

    # Test 1: Health
    results['health'] = test_health()
    if not results['health']:
        print("\n[ABORT] Server not healthy. Cannot continue tests.")
        return

    time.sleep(1)

    # Test 2: Detailed Health
    results['detailed_health'] = test_detailed_health()
    time.sleep(1)

    # Test 3: Documents
    results['documents'] = test_rag_documents()
    time.sleep(1)

    # Test 4: Simple Presentation
    results['simple_presentation'] = test_simple_presentation()
    time.sleep(2)

    # Test 5: Financial Presentation with RAG
    results['financial_presentation'] = test_financial_presentation()

    # Summary
    print_section("TEST SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n[SUCCESS] All tests passed! ConvoSynth is fully operational.")
    else:
        print("\n[PARTIAL] Some tests failed. Check details above.")

    print("\nGenerated Files:")
    if Path("test_simple_output.html").exists():
        print("  - test_simple_output.html (simple presentation)")
    if Path("test_financial_output.html").exists():
        print("  - test_financial_output.html (financial presentation)")

    print("\nNext Steps:")
    print("  1. Open generated HTML files in browser")
    print("  2. Check server logs for detailed execution trace")
    print("  3. Try API docs: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    main()
