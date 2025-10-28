"""Comprehensive API Testing Script for ConvoSynth with RAG Integration.

This script tests all API endpoints including:
- Health checks
- RAG queries
- Presentation generation

Run this after starting the server with: python run.py
"""
import requests
import json
import time
from typing import Dict, Any


# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"      {details}")


def test_root_endpoint():
    """Test root endpoint."""
    print_section("TEST 1: Root Endpoint")

    try:
        response = requests.get(BASE_URL)
        data = response.json()

        passed = (
            response.status_code == 200 and
            data.get("name") == "ConvoSynth API" and
            data.get("status") == "operational"
        )

        print_test("Root endpoint accessible", passed)
        print(f"      Response: {json.dumps(data, indent=2)}")
        return passed

    except Exception as e:
        print_test("Root endpoint accessible", False, f"Error: {e}")
        return False


def test_health_endpoints():
    """Test health check endpoints."""
    print_section("TEST 2: Health Check Endpoints")

    results = []

    # Test basic health
    try:
        response = requests.get(f"{API_V1}/health")
        data = response.json()

        passed = response.status_code == 200 and data.get("status") == "healthy"
        print_test("Basic health check", passed)
        results.append(passed)

    except Exception as e:
        print_test("Basic health check", False, f"Error: {e}")
        results.append(False)

    # Test detailed health
    try:
        response = requests.get(f"{API_V1}/health/detailed")
        data = response.json()

        passed = response.status_code == 200
        print_test("Detailed health check", passed)

        if passed:
            print(f"\n      Components:")
            for comp, status in data.get("components", {}).items():
                print(f"        - {comp}: {status}")

            print(f"\n      Agents:")
            for agent, status in data.get("agents", {}).items():
                print(f"        - {agent}: {status}")

            print(f"\n      RAG Stats:")
            rag_stats = data.get("rag", {})
            for key, value in rag_stats.items():
                print(f"        - {key}: {value}")

        results.append(passed)

    except Exception as e:
        print_test("Detailed health check", False, f"Error: {e}")
        results.append(False)

    # Test ping
    try:
        response = requests.get(f"{API_V1}/ping")
        data = response.json()

        passed = response.status_code == 200 and data.get("message") == "pong"
        print_test("Ping endpoint", passed)
        results.append(passed)

    except Exception as e:
        print_test("Ping endpoint", False, f"Error: {e}")
        results.append(False)

    return all(results)


def test_rag_health():
    """Test RAG health endpoint."""
    print_section("TEST 3: RAG Health Check")

    try:
        response = requests.get(f"{API_V1}/rag/health")
        data = response.json()

        passed = response.status_code == 200 and data.get("healthy") == True
        print_test("RAG health check", passed)

        print(f"\n      RAG Status:")
        print(f"        - Status: {data.get('status')}")
        print(f"        - Healthy: {data.get('healthy')}")
        print(f"        - Initialized: {data.get('initialized')}")
        print(f"        - Working Dir: {data.get('working_dir')}")
        print(f"        - Parser: {data.get('parser')}")

        return passed

    except Exception as e:
        print_test("RAG health check", False, f"Error: {e}")
        return False


def test_rag_stats():
    """Test RAG stats endpoint."""
    print_section("TEST 4: RAG Statistics")

    try:
        response = requests.get(f"{API_V1}/rag/stats")
        data = response.json()

        passed = response.status_code == 200 and data.get("initialized") == True
        print_test("RAG stats retrieval", passed)

        print(f"\n      RAG Configuration:")
        for key, value in data.items():
            print(f"        - {key}: {value}")

        return passed

    except Exception as e:
        print_test("RAG stats retrieval", False, f"Error: {e}")
        return False


def test_rag_queries():
    """Test RAG query endpoint with various queries."""
    print_section("TEST 5: RAG Query Tests")

    test_queries = [
        {
            "name": "Revenue Query",
            "query": "What is Becton Dickinson's revenue for Q3 2025?",
            "mode": "hybrid",
            "expected_min_length": 500
        },
        {
            "name": "Growth Analysis",
            "query": "Show revenue growth rate and year-over-year comparison",
            "mode": "hybrid",
            "expected_min_length": 1000
        },
        {
            "name": "Financial Metrics",
            "query": "Operating margin, earnings per share, and profitability metrics",
            "mode": "hybrid",
            "expected_min_length": 1000
        },
        {
            "name": "Global Query",
            "query": "Key strategic initiatives and business outlook",
            "mode": "global",
            "expected_min_length": 500
        },
    ]

    results = []

    for i, test in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] {test['name']}")
        print(f"      Query: '{test['query']}'")
        print(f"      Mode: {test['mode']}")

        try:
            payload = {
                "query": test['query'],
                "mode": test['mode']
            }

            start_time = time.time()
            response = requests.post(f"{API_V1}/rag/query", json=payload)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                context_length = data.get("context_length", 0)

                passed = context_length >= test['expected_min_length']

                if passed:
                    print(f"      [OK] Retrieved {context_length} characters in {elapsed:.2f}s")

                    # Show preview
                    context = data.get("context", "")
                    preview = context[:200] + "..." if len(context) > 200 else context
                    print(f"\n      Preview:")
                    for line in preview.split("\n")[:3]:
                        print(f"        {line}")

                    results.append(True)
                else:
                    print(f"      [FAIL] Expected >= {test['expected_min_length']} chars, got {context_length}")
                    results.append(False)
            else:
                print(f"      [FAIL] HTTP {response.status_code}: {response.text}")
                results.append(False)

        except Exception as e:
            print(f"      [ERROR] {e}")
            results.append(False)

    success_rate = (sum(results) / len(results) * 100) if results else 0
    print(f"\n      Success Rate: {sum(results)}/{len(results)} ({success_rate:.1f}%)")

    return all(results)


def test_presentation_generation():
    """Test presentation generation with RAG."""
    print_section("TEST 6: Presentation Generation")

    test_requests = [
        {
            "name": "Simple Financial Overview",
            "user_input": "Create a Q3 2025 earnings presentation for Becton Dickinson",
            "slide_count": 8,
            "presentation_type": "financial_overview"
        },
        {
            "name": "Revenue Focus",
            "user_input": "Generate a presentation focusing on revenue growth and performance metrics",
            "slide_count": 6,
            "presentation_type": "financial_overview",
            "focus_areas": ["revenue", "growth", "performance"]
        }
    ]

    results = []

    for i, test in enumerate(test_requests, 1):
        print(f"\n[{i}/{len(test_requests)}] {test['name']}")
        print(f"      Input: '{test['user_input']}'")
        print(f"      Slides: {test['slide_count']}")

        try:
            payload = {
                "user_input": test['user_input'],
                "slide_count": test['slide_count'],
                "presentation_type": test['presentation_type']
            }

            if "focus_areas" in test:
                payload["focus_areas"] = test["focus_areas"]

            print(f"      Generating presentation (this may take 30-60 seconds)...")

            start_time = time.time()
            response = requests.post(
                f"{API_V1}/presentations/generate",
                json=payload,
                timeout=120  # 2 minute timeout
            )
            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                status = data.get("status")

                if status == "completed":
                    total_slides = data.get("total_slides", 0)
                    html_length = len(data.get("presentation_html", ""))

                    passed = total_slides > 0 and html_length > 1000

                    if passed:
                        print(f"      [OK] Generated {total_slides} slides in {elapsed:.1f}s")
                        print(f"      HTML Size: {html_length:,} characters")

                        metadata = data.get("metadata", {})
                        if metadata:
                            print(f"      Metadata:")
                            for key, value in metadata.items():
                                print(f"        - {key}: {value}")

                        # Save HTML for inspection
                        session_id = data.get("session_id")
                        filename = f"output/presentation_{session_id}.html"

                        try:
                            import os
                            os.makedirs("output", exist_ok=True)
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(data.get("presentation_html", ""))
                            print(f"      Saved to: {filename}")
                        except Exception as e:
                            print(f"      Could not save HTML: {e}")

                        results.append(True)
                    else:
                        print(f"      [FAIL] Invalid output: {total_slides} slides, {html_length} chars")
                        results.append(False)
                else:
                    error = data.get("error", "Unknown error")
                    print(f"      [FAIL] Status: {status}, Error: {error}")
                    results.append(False)
            else:
                print(f"      [FAIL] HTTP {response.status_code}: {response.text}")
                results.append(False)

        except requests.Timeout:
            print(f"      [TIMEOUT] Request took longer than 2 minutes")
            results.append(False)
        except Exception as e:
            print(f"      [ERROR] {e}")
            results.append(False)

    success_rate = (sum(results) / len(results) * 100) if results else 0
    print(f"\n      Success Rate: {sum(results)}/{len(results)} ({success_rate:.1f}%)")

    return all(results)


def main():
    """Run all API tests."""
    print("\n" + "=" * 80)
    print("  CONVOSYNTH API COMPREHENSIVE TEST SUITE")
    print("  Testing RAG Integration with FastAPI Backend")
    print("=" * 80)

    print(f"\nTarget: {BASE_URL}")
    print(f"Make sure the server is running: python run.py\n")

    # Wait for user confirmation
    input("Press Enter to start tests...")

    test_results = {}

    # Run tests
    test_results["Root Endpoint"] = test_root_endpoint()
    test_results["Health Checks"] = test_health_endpoints()
    test_results["RAG Health"] = test_rag_health()
    test_results["RAG Stats"] = test_rag_stats()
    test_results["RAG Queries"] = test_rag_queries()
    test_results["Presentation Generation"] = test_presentation_generation()

    # Summary
    print_section("TEST SUMMARY")

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%\n")

    print("Test Results:")
    for test_name, passed in test_results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    print("\n" + "=" * 80)

    if all(test_results.values()):
        print("  [SUCCESS] All tests passed!")
        print("  Your ConvoSynth API with RAG is fully operational!")
    else:
        print("  [PARTIAL] Some tests failed")
        print("  Check the output above for details")

    print("=" * 80 + "\n")

    return all(test_results.values())


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
