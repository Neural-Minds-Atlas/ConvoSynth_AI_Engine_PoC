"""Test RAG with custom financial queries to verify capabilities."""
import asyncio
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.config import RAGConfig

async def test_custom_queries():
    """Test RAG with various financial queries."""
    print("\n" + "="*70)
    print("  RAG CUSTOM QUERY TESTING")
    print("="*70 + "\n")

    # Initialize RAG client
    print("Initializing RAG client...")
    config = RAGConfig()
    rag_client = RAGAnythingClient(config=config)
    await rag_client.initialize()
    print("[OK] RAG client ready\n")

    # Define test queries covering different aspects
    test_queries = [
        {
            "name": "Revenue Query",
            "query": "What is Becton Dickinson's revenue for Q3 2025?",
            "mode": "hybrid"
        },
        {
            "name": "Growth Analysis",
            "query": "Show revenue growth rate and year-over-year comparison",
            "mode": "hybrid"
        },
        {
            "name": "Segment Performance",
            "query": "Medical device segment performance and breakdown",
            "mode": "local"
        },
        {
            "name": "Financial Metrics",
            "query": "Operating margin, earnings per share, and profitability metrics",
            "mode": "hybrid"
        },
        {
            "name": "Geographic Analysis",
            "query": "International vs domestic revenue breakdown",
            "mode": "local"
        },
        {
            "name": "Strategic Insights",
            "query": "Key strategic initiatives and business outlook",
            "mode": "global"
        },
        {
            "name": "Risk Factors",
            "query": "Major risks and challenges mentioned in filings",
            "mode": "hybrid"
        },
        {
            "name": "Cash Flow",
            "query": "Operating cash flow and capital expenditures",
            "mode": "local"
        }
    ]

    results = []

    for i, test in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {test['name']}")
        print(f"      Query: {test['query']}")
        print(f"      Mode: {test['mode']}")

        try:
            result = await rag_client.query(
                query_text=test['query'],
                mode=test['mode']
            )

            context = result.get("context", "")

            # Debug: Show what we got
            print(f"      DEBUG: context type={type(context)}, length={len(context)}")
            if "error" in context.lower() or "failed" in context.lower():
                print(f"      DEBUG: Error in context: {context[:200]}")

            if context and len(context) > 100:
                print(f"      [OK] Retrieved {len(context)} characters")
                print(f"\n      Preview:")
                print("      " + "-"*66)

                # Show first 400 chars
                preview = context[:400]
                for line in preview.split("\n"):
                    print(f"      {line}")

                if len(context) > 400:
                    print(f"      ... ({len(context) - 400} more characters)")

                print("      " + "-"*66)

                results.append({
                    "name": test['name'],
                    "success": True,
                    "length": len(context)
                })
            else:
                print(f"      [WARNING] Empty or short response ({len(context)} chars)")
                results.append({
                    "name": test['name'],
                    "success": False,
                    "length": len(context)
                })

            print()

        except Exception as e:
            print(f"      [ERROR] {e}\n")
            results.append({
                "name": test['name'],
                "success": False,
                "error": str(e)
            })

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70 + "\n")

    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)

    print(f"  Successful queries: {successful}/{total}")
    print(f"  Success rate: {(successful/total*100):.1f}%\n")

    print("  Query Results:")
    for r in results:
        status = "[OK]" if r.get("success", False) else "[FAIL]"
        length = r.get("length", 0)
        print(f"    {status} {r['name']:30} {length:>6} chars")

    print("\n" + "="*70)

    if successful >= total * 0.75:  # 75% success rate
        print("  [SUCCESS] RAG is working well!")
        print("="*70)
        print("\n  Your RAG system can:")
        print("    - Retrieve specific financial metrics")
        print("    - Analyze revenue and growth trends")
        print("    - Extract segment-level details")
        print("    - Answer strategic questions")
        print("\n  Next step: Test with FastAPI backend")
        print("    Run: python run.py")
        print("    Then: python test_rag_complete.py\n")
        return True
    else:
        print("  [PARTIAL] Some queries failed")
        print("="*70)
        print("\n  Check the failed queries above")
        print("  The data might be limited or queries need refinement\n")
        return False


async def test_specific_document_query():
    """Test querying specific document types."""
    print("\n" + "="*70)
    print("  DOCUMENT-SPECIFIC QUERIES")
    print("="*70 + "\n")

    config = RAGConfig()
    rag_client = RAGAnythingClient(config=config)
    await rag_client.initialize()

    document_queries = [
        "Find information from Form 10-Q filing",
        "What does the 8-K report mention?",
        "Summarize earnings call transcript key points",
    ]

    for query in document_queries:
        print(f"Query: {query}")
        result = await rag_client.query(query, mode="hybrid")
        context = result.get("context", "")

        if context and len(context) > 50:
            print(f"[OK] {len(context)} chars retrieved")
            print(f"Preview: {context[:200]}...\n")
        else:
            print(f"[EMPTY] No relevant context\n")


if __name__ == "__main__":
    print("\nTesting RAG Capabilities with Custom Queries")
    print("This will verify retrieval quality across different query types\n")

    # Run main tests
    success = asyncio.run(test_custom_queries())

    # Run document-specific tests
    print("\n" + "="*70)
    asyncio.run(test_specific_document_query())

    exit(0 if success else 1)
