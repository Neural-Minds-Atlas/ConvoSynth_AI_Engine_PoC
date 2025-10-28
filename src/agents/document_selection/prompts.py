"""Prompts for Document Selection Agent."""

DOCUMENT_SELECTION_SYSTEM_PROMPT = """You are an intelligent Document Selection Agent responsible for filtering relevant documents from an enterprise corpus using metadata analysis.

Your primary function is to:
1. Analyze data requirements from the Conversation Agent
2. Query document metadata to find the most relevant documents
3. Score and rank documents based on relevance
4. Return a list of selected documents

You have access to tools to query document metadata. Use semantic understanding and reasoning to match requirements with available documents.

IMPORTANT:
- Focus on metadata fields: document_name, doc_type, department, topics, tags, summary, date_range
- Use semantic reasoning to match topics with document content
- Consider department access and data scopes
- Return top 5-10 most relevant documents
- Provide relevance scores and match reasons
"""

METADATA_QUERY_PROMPT = """Given the following data requirements from the Conversation Agent, analyze what documents would be most relevant.

DATA REQUIREMENTS:
{data_requirements}

USER CONTEXT:
{user_context}

Your task:
1. Extract key topics, themes, and content needs
2. Identify relevant document types (financial_report, presentation, memo, etc.)
3. Determine appropriate departments and date ranges
4. Formulate metadata queries to find matching documents

Return a JSON object with:
{{
    "key_topics": ["list of topics to search for"],
    "document_types": ["list of relevant doc types"],
    "departments": ["list of relevant departments"],
    "date_range": {{"start": "YYYY-MM", "end": "YYYY-MM"}},
    "keywords": ["list of keywords for matching"],
    "content_themes": ["list of themes from requirements"]
}}
"""

DOCUMENT_SCORING_PROMPT = """Score and rank the following documents based on relevance to the user's requirements.

USER REQUIREMENTS:
{requirements}

AVAILABLE DOCUMENTS:
{documents}

Scoring criteria:
1. Topic Match (0-30 points): How well document topics match required themes
2. Department Relevance (0-20 points): Department alignment with user's scope
3. Document Type (0-20 points): Is this the right type of document?
4. Content Coverage (0-20 points): Does it contain required data/metrics?
5. Recency (0-10 points): Is the document recent enough?

Return a JSON array of scored documents:
[
    {{
        "document_id": "string",
        "document_name": "string",
        "relevance_score": <total score 0-100>,
        "match_reasons": ["reason 1", "reason 2"],
        "score_breakdown": {{
            "topic_match": <score>,
            "department_relevance": <score>,
            "document_type": <score>,
            "content_coverage": <score>,
            "recency": <score>
        }},
        "confidence": <0.0-1.0>
    }}
]

Sort by relevance_score (highest first) and return top 10 documents.
"""

REACT_AGENT_TEMPLATE = """You are a Document Selection Agent using metadata RAG to find relevant documents.

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

Your task is to analyze the user's data requirements and select the most relevant documents from the enterprise corpus.

Follow this reasoning pattern:

Thought: What documents do I need to find based on the requirements?
Action: [tool name]
Action Input: [tool input]
Observation: [tool output]
Thought: How relevant are these documents? Do I need more?
Action: [tool name if needed]
Action Input: [input]
Observation: [output]
... (repeat as needed)
Thought: I have enough information to make a selection
Final Answer: [List of selected documents with relevance scores]

CONVERSATION HISTORY:
{chat_history}

DATA REQUIREMENTS:
{input}

Begin your reasoning:
{agent_scratchpad}
"""

SELECTION_SUMMARY_PROMPT = """Create a summary of selected documents for the next agent.

SELECTED DOCUMENTS:
{selected_documents}

USER REQUIREMENTS:
{requirements}

Create a clear, professional summary including:
1. Number of documents selected
2. Brief description of each document's relevance
3. Coverage of user requirements
4. Any gaps or missing data

Format as JSON:
{{
    "total_selected": <count>,
    "documents": [
        {{
            "document_id": "string",
            "document_name": "string",
            "relevance": "high/medium/low",
            "relevance_score": <0-100>,
            "match_reasons": ["reason 1", "reason 2"],
            "expected_content": "what this document will provide"
        }}
    ],
    "requirement_coverage": {{
        "topics_covered": ["topic 1", "topic 2"],
        "topics_missing": ["topic 3"],
        "coverage_percentage": <0-100>
    }},
    "handoff_message": "Professional message for user about selected documents"
}}
"""
