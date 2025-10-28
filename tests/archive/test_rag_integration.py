"""Test RAG integration end-to-end.

This script tests:
1. Document ingestion
2. RAG retrieval
3. Presentation generation with real financial data
"""
import asyncio
import sys
from pathlib import Path
import time

print("\n" + "="*70)
print("  CONVOSYNTH RAG INTEGRATION TEST")
print("="*70 + "\n")


async def test_rag_pipeline():
    """Test complete RAG pipeline."""
    from src.rag_anything.client import RAGAnythingClient
    from src.rag_anything.config import RAGConfig
    from src.agents.rag_engine import RAGEngineAgent
    from src.agents.base import AgentRequest

    # Step 1: Initialize RAG client
    print("[1/5] Initializing RAG-Anything client...")
    config = RAGConfig()
    rag_client = RAGAnythingClient(config=config)

    try:
        await rag_client.initialize()
        print("      [OK] RAG-Anything initialized\n")
    except Exception as e:
        print(f"      [ERROR] {e}")
        print("\nRun: pip install 'raganything[all]'\n")
        return False

    # Step 2: Check if documents exist
    print("[2/5] Checking for financial documents...")
    doc_dir = Path("data/financial_samples")

    if not doc_dir.exists():
        print(f"      [ERROR] Directory not found: {doc_dir}")
        return False

    pdf_files = list(doc_dir.glob("*.pdf"))
    print(f"      Found {len(pdf_files)} PDF documents")

    if len(pdf_files) == 0:
        print("      [ERROR] No PDF documents found")
        return False

    # Check if documents have been ingested
    print("\n      Checking if documents have been ingested...")
    storage_dir = config.working_dir

    if not storage_dir.exists() or not any(storage_dir.iterdir()):
        print("      [WARNING] Documents not ingested yet!")
        print("\n      Please run first: python ingest_financial_documents.py")
        print("      This test requires documents to be pre-processed.\n")
        return False
    else:
        print("      [OK] RAG storage exists\n")

    # Step 3: Test simple query
    print("[3/5] Testing simple RAG query...")
    test_query = "Becton Dickinson Q3 2025 revenue and earnings"
    print(f"      Query: '{test_query}'")

    start_time = time.time()
    try:
        result = await rag_client.query(
            query_text=test_query,
            mode="hybrid"
        )
        elapsed = time.time() - start_time

        context = result.get("context", "")
        if context and len(context) > 50:
            print(f"      [OK] Retrieved {len(context)} characters in {elapsed:.2f}s")
            print(f"\n      Context preview:")
            print(f"      {'-'*66}")
            preview = context[:300] + "..." if len(context) > 300 else context
            for line in preview.split("\n"):
                print(f"      {line}")
            print(f"      {'-'*66}\n")
        else:
            print(f"      [WARNING] Context is empty or too short ({len(context)} chars)")
            print("      This might mean documents weren't properly indexed\n")
            return False

    except Exception as e:
        print(f"      [ERROR] Query failed: {e}\n")
        return False

    # Step 4: Test RAG Engine Agent
    print("[4/5] Testing RAG Engine Agent...")
    rag_engine = RAGEngineAgent(rag_client=rag_client)

    request = AgentRequest(
        user_input="Create financial presentation about Q3 2025 results",
        context={
            "query_output": {
                "query_context": {
                    "primary_focus": "Q3 2025 financial results for Becton Dickinson"
                },
                "entities": {
                    "company": ["Becton Dickinson", "BDX"],
                    "time_period": ["Q3 2025"],
                    "metrics": ["revenue", "earnings", "growth"]
                },
                "search_strategy": {
                    "vector_weight": 0.7,
                    "graph_weight": 0.3
                }
            },
            "documents": []
        }
    )

    start_time = time.time()
    try:
        result = await rag_engine.execute(request)
        elapsed = time.time() - start_time

        retrieved_context = result.get("retrieved_context", "")
        sources = result.get("sources", [])
        findings = result.get("key_findings", [])

        print(f"      [OK] Agent executed in {elapsed:.2f}s")
        print(f"      - Retrieved context: {len(retrieved_context)} chars")
        print(f"      - Sources: {len(sources)}")
        print(f"      - Key findings: {len(findings)}")

        if findings:
            print(f"\n      Key findings:")
            for i, finding in enumerate(findings[:3], 1):
                print(f"        {i}. {finding}")

        print()

    except Exception as e:
        print(f"      [ERROR] Agent execution failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Test full workflow integration
    print("[5/5] Testing workflow integration...")
    from src.orchestration import SequentialWorkflow

    workflow = SequentialWorkflow(rag_client=rag_client)

    try:
        result = await workflow.execute(
            user_input="Create a 5-slide presentation about Becton Dickinson Q3 2025 financial performance",
            documents=None,
            user_preferences={"slide_count": 5}
        )

        presentation_html = result.get("presentation", {}).get("html", "")
        workflow_time = result.get("total_time", 0)

        if presentation_html:
            print(f"      [OK] Workflow completed in {workflow_time:.2f}s")
            print(f"      - Generated HTML: {len(presentation_html)} chars")
            print(f"      - Presentation ready!\n")
            return True
        else:
            print(f"      [WARNING] No presentation HTML generated")
            print(f"      Result: {result}\n")
            return False

    except Exception as e:
        print(f"      [ERROR] Workflow failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run RAG integration tests."""
    try:
        success = asyncio.run(test_rag_pipeline())

        print("="*70)
        if success:
            print("  [SUCCESS] RAG PIPELINE IS FULLY FUNCTIONAL!")
            print("="*70)
            print("\n  Next steps:")
            print("  1. Start server: python run.py")
            print("  2. Test API: python test_rag_complete.py")
            print("  3. Try web UI: http://localhost:8000/docs\n")
            sys.exit(0)
        else:
            print("  [PARTIAL] Some tests failed")
            print("="*70)
            print("\n  If documents aren't ingested:")
            print("    Run: python ingest_financial_documents.py")
            print("\n  If other errors occurred:")
            print("    Check the error messages above\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Test interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
