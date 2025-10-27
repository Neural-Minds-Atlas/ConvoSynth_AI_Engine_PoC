"""Direct test of RAG query to debug issues."""
import asyncio
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.config import RAGConfig

async def test_direct():
    """Test query with full debugging."""
    config = RAGConfig()
    rag_client = RAGAnythingClient(config=config)

    print("Initializing...")
    await rag_client.initialize()
    print(f"Initialized: {rag_client._initialized}")
    print(f"RAG object: {rag_client._rag}")
    print(f"Has LightRAG: {hasattr(rag_client._rag, 'lightrag')}")

    if hasattr(rag_client._rag, 'lightrag'):
        print(f"LightRAG instance: {rag_client._rag.lightrag}")

    print("\nTesting query...")

    try:
        # Call through our client wrapper (which now bypasses RAG-Anything bug)
        result = await rag_client.query(
            "Becton Dickinson revenue",
            mode="hybrid"
        )

        print(f"\nResult type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

        if isinstance(result, dict):
            context = result.get("context", "")
            print(f"\nContext type: {type(context)}")
            print(f"Context length: {len(context)}")
            if len(context) > 0:
                print(f"\nFirst 500 chars:\n{context[:500]}")
                print(f"\n[SUCCESS] Query returned {len(context)} characters!")
            else:
                print(f"\n[EMPTY] No context returned")
        else:
            print(f"\nUnexpected result format: {result}")

    except Exception as e:
        print(f"\nError during query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct())
