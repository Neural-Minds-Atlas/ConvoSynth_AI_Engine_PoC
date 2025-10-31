# Cost Optimization Guide for RAG Ingestion

## Problem Summary

You're spending $28 in 40 minutes on Claude API calls during document ingestion. This is because:

1. **LLMs are used for entity/relationship extraction** during ingestion to build the knowledge graph
2. For large documents with many chunks, this can result in hundreds of LLM calls
3. Claude Sonnet 4 is expensive for high-volume processing

## Two Solutions

---

## Solution 1: Switch from Claude to Cohere for Ingestion

Cohere is **significantly cheaper** than Claude for knowledge graph building:

- **Cohere Command-R**: ~$0.50 per million tokens (input), $1.50 (output)
- **Claude Sonnet 4**: ~$3 per million tokens (input), $15 (output)

### ✅ Already Implemented in Your Codebase!

Your system **already supports Cohere** for ingestion. You just need to use it:

### How to Use Cohere for Ingestion

#### Option A: Set Server Default (Recommended)

In your `.env` file:

```bash
# Set Ollama to false to use Cohere by default
USE_OLLAMA=false

# Ensure Cohere API key is set
COHERE_API_KEY=your_cohere_api_key_here
```

Then restart your server and ingest documents normally. The system will use Cohere automatically.

#### Option B: Specify in API Request

When calling `/api/v1/documents/ingest`, add `model_provider`:

```json
{
  "file_ids": ["file1", "file2"],
  "model_provider": "cohere" // <-- Add this
}
```

### Code Reference

The ingestion routing happens in `src/api/routes/documents.py`:

```python
@router.post("/ingest", response_model=DocumentIngestionResponse)
async def ingest_documents(req: DocumentIngestionRequest, ...):
    # Model provider selection logic
    if req.model_provider:
        model_provider = req.model_provider.lower()  # Use from request
    else:
        model_provider = "ollama" if settings.use_ollama else "cohere"  # Default

    # Valid options: "ollama", "cohere", "claude"
```

### Verify Cohere is Being Used

Check your logs for:

```
ingestion_model_provider_selected provider=cohere
```

---

## Solution 2: Disable Knowledge Graph (Vector-Only Storage)

If you don't need the knowledge graph and only want vector search, you can skip entity extraction entirely.

### ⚠️ Warning: This Requires Code Modification

This option removes the knowledge graph capability, giving you **pure vector search only**.

### What You Lose

- ❌ Entity and relationship extraction
- ❌ Knowledge graph traversal
- ❌ Graph-based reasoning
- ❌ Hybrid (vector + graph) retrieval

### What You Keep

- ✅ Document chunking
- ✅ Vector embeddings (cheap, uses OpenAI text-embedding-3-small)
- ✅ Semantic search via vectors
- ✅ Fast retrieval

### Implementation Steps

#### Step 1: Find RAG-Anything Ingestion Logic

The ingestion happens in `src/rag_anything/client.py` → `process_document()` method.

Currently, it calls:

```python
await self._rag.ainsert(...)  # This triggers entity extraction internally
```

#### Step 2: Bypass Entity Extraction

You need to modify LightRAG's configuration to **skip entity extraction**.

**Option A: Disable at LightRAG Level**

In `src/rag_anything/client.py`, when initializing `RAGAnything`, add a flag:

```python
# In the initialize() method, around line 85-110
rag_config = RAGAnythingConfig(
    working_dir=str(self.config.working_dir),
    parser="mineru",
    parse_method="auto",
    enable_image_processing=True,
    enable_table_processing=True,
    # ADD THIS:
    disable_kg_extraction=True,  # Skip knowledge graph building
)
```

**However**, check if `RAGAnythingConfig` or LightRAG supports this flag. If not, you'll need Option B.

**Option B: Replace `ainsert` with Vector-Only Insertion**

This is more invasive. You'd need to:

1. Chunk the document yourself (use `chunking_by_token_size`)
2. Generate embeddings for chunks
3. Store chunks directly in vector storage (skip graph storage)

Example pseudo-code:

```python
# In process_document() method
async def process_document(self, document_path: Path) -> Dict[str, Any]:
    # Parse document
    doc_text = await self._parse_document(document_path)

    # Chunk text
    chunks = chunking_by_token_size(
        doc_text,
        chunk_size=1200,
        overlap_size=100
    )

    # Generate embeddings (cheap)
    embeddings = await self._embed_chunks(chunks)

    # Store in vector DB only (skip LLM extraction)
    await self._store_vectors_only(chunks, embeddings)

    return {"status": "success", "chunks": len(chunks)}
```

This completely bypasses LightRAG's `ainsert` and avoids LLM calls.

---

## Recommendation

### 🎯 **Start with Solution 1 (Switch to Cohere)**

**Why:**

- ✅ Already implemented in your codebase
- ✅ No code changes required
- ✅ ~10x cheaper than Claude
- ✅ Keeps all RAG capabilities (hybrid search, knowledge graph)
- ✅ Easy to revert

**Steps:**

1. Set `USE_OLLAMA=false` in `.env`
2. Ensure `COHERE_API_KEY` is set
3. Restart server
4. Ingest documents

**Expected Cost Reduction:** $28 → ~$3-5 (estimated 80-85% savings)

### 🔧 **Consider Solution 2 Only If:**

- You don't need knowledge graph features
- You only need basic semantic search
- You want **absolute minimum cost** (embeddings are ~$0.02 per million tokens)
- You're willing to lose graph-based reasoning

---

## Cost Comparison Table

| Approach             | Cost (40 min) | Knowledge Graph | Complexity                   |
| -------------------- | ------------- | --------------- | ---------------------------- |
| **Claude Sonnet 4**  | $28           | ✅ Yes          | Low                          |
| **Cohere Command-R** | ~$3-5         | ✅ Yes          | Low (already supported)      |
| **Vector-Only**      | ~$0.50        | ❌ No           | High (requires code changes) |

---

## Testing Your Changes

### Verify Cohere is Working

1. Start ingestion
2. Check logs for:
   ```
   rag_client_initialized_for_ingestion model_provider=cohere
   ```
3. Monitor Cohere API usage at https://dashboard.cohere.com/

### Monitor Costs

- **Cohere Dashboard**: Track API usage in real-time
- **OpenAI Dashboard**: Track embedding costs (should be minimal)

---

## Additional Cost Optimizations

### 1. Adjust Chunking Parameters

Larger chunks = fewer LLM calls:

```python
# In RAG config
chunk_size = 1200  # Increase from default (if smaller)
overlap_size = 100
```

### 2. Process Documents in Batches

Spread ingestion over time to avoid burst costs.

### 3. Use Cohere's Batch API (If Available)

Some providers offer batch processing discounts.

### 4. Cache LLM Responses

LightRAG already caches responses in `kv_store_llm_response_cache.json`. Ensure this is enabled.

---

## Questions?

- **Which model provider am I currently using?** → Check logs for `model_provider=`
- **How do I switch providers mid-project?** → Change `.env` or use `model_provider` in API request
- **Can I use Ollama for free?** → Yes, if you have a local GPU server, but requires setup

---

## Summary

✅ **Immediate Action**: Switch to Cohere for 80-85% cost savings with zero code changes  
🔧 **Advanced Option**: Disable knowledge graph for 98% cost savings (but loses graph features)  
📊 **Monitor**: Track costs at Cohere/OpenAI dashboards

Your codebase is well-designed for this! The model provider abstraction is already in place.
