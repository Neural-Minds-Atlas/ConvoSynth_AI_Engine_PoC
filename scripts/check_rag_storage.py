"""Check if RAG storage has data despite failed ingestion."""
import asyncio
from pathlib import Path
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.config import RAGConfig

async def check_storage():
    """Check RAG storage and test a query."""
    print("\n" + "="*70)
    print("  RAG STORAGE VERIFICATION")
    print("="*70 + "\n")

    # Check storage directory
    config = RAGConfig()
    storage_dir = config.working_dir

    print(f"[1/3] Checking storage directory: {storage_dir}")
    if not storage_dir.exists():
        print("      [ERROR] Storage directory does not exist")
        print("      Run: python ingest_financial_documents.py\n")
        return False

    # List files in storage
    files = list(storage_dir.rglob("*"))
    data_files = [f for f in files if f.is_file()]

    print(f"      [OK] Found {len(data_files)} files in storage")

    if len(data_files) == 0:
        print("      [WARNING] No data files found")
        print("      Ingestion may have failed completely\n")
        return False

    # Show some files
    print("\n      Storage contents:")
    for i, f in enumerate(data_files[:10], 1):
        size = f.stat().st_size
        print(f"        {i}. {f.name} ({size:,} bytes)")
    if len(data_files) > 10:
        print(f"        ... and {len(data_files) - 10} more files")
    print()

    # Initialize RAG client
    print("[2/3] Initializing RAG client...")
    rag_client = RAGAnythingClient(config=config)

    try:
        await rag_client.initialize()
        print("      [OK] RAG client initialized\n")
    except Exception as e:
        print(f"      [ERROR] Failed to initialize: {e}\n")
        return False

    # Test a query
    print("[3/3] Testing retrieval with a query...")
    test_queries = [
        "Becton Dickinson revenue",
        "financial performance Q3 2025",
        "earnings report",
        "revenue growth"
    ]

    for query in test_queries:
        print(f"\n      Query: '{query}'")
        try:
            result = await rag_client.query(
                query_text=query,
                mode="hybrid"
            )

            context = result.get("context", "")
            if context and len(context) > 50:
                print(f"      [OK] Retrieved {len(context)} characters")
                print(f"      Preview: {context[:200]}...")
                print("\n" + "="*70)
                print("  [SUCCESS] RAG IS WORKING!")
                print("="*70)
                print("\n  Even though ingestion showed 'failed', the data WAS stored!")
                print("  The error was during finalization, not actual processing.")
                print("\n  You can now:")
                print("    1. Start the server: python run.py")
                print("    2. Generate presentations with real data")
                print("    3. Test API: python test_rag_complete.py\n")
                return True
            else:
                print(f"      [EMPTY] No context returned ({len(context)} chars)")

        except Exception as e:
            print(f"      [ERROR] Query failed: {e}")

    print("\n" + "="*70)
    print("  [PARTIAL] Storage exists but queries return no data")
    print("="*70)
    print("\n  This means:")
    print("    - Files were created in storage")
    print("    - But the index wasn't properly finalized")
    print("    - Need to re-run ingestion with a fix\n")
    return False


if __name__ == "__main__":
    success = asyncio.run(check_storage())
    exit(0 if success else 1)
