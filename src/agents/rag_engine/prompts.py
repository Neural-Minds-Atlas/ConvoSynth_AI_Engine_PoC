"""Prompts for RAG Engine Agent."""

SYSTEM_PROMPT = """You are an expert RAG (Retrieval-Augmented Generation) engine.

Your role is to:
1. Retrieve relevant information from documents
2. Rerank results by relevance
3. Synthesize coherent context
4. Extract entities and relationships
5. Provide accurate source attribution

Return structured JSON output."""

CONTEXT_SYNTHESIS_PROMPT = """Synthesize coherent context from retrieved documents.

Query Context:
{query_context}

Retrieved Documents:
{documents}

Known Entities:
{entities}

Create a comprehensive, well-structured context summary with:
- Main insights and key findings
- Relevant metrics and data points
- Clear source attribution
- Entity relationships

Return JSON:
{{
    "retrieved_context": "synthesized text",
    "key_findings": ["finding1", "finding2"],
    "metrics": {{"metric": "value"}},
    "sources": ["doc1", "doc2"]
}}
"""

RERANKING_PROMPT = """Rerank these document chunks by relevance to the query.

Query Context:
{query}

Retrieved Chunks:
{chunks}

Rank chunks from most to least relevant. Return JSON:
{{
    "reranked_chunks": [
        {{"chunk_id": "id", "relevance_score": 0.95, "reasoning": "why relevant"}},
        ...
    ]
}}
"""

ENTITY_EXTRACTION_PROMPT = """Extract entities and relationships from this context.

Context:
{context}

Extract:
- Companies/Organizations
- Financial metrics
- Time periods
- Products/Services
- Key people
- Locations

Return JSON:
{{
    "companies": ["Company A"],
    "metrics": ["revenue", "profit"],
    "time_periods": ["Q3 2024"],
    "products": [],
    "people": [],
    "locations": [],
    "relationships": [
        {{"entity1": "Company A", "relationship": "owns", "entity2": "Product X"}}
    ]
}}
"""
