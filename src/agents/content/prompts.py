"""
Content Agent Prompts
Comprehensive prompts for content generation with financial analysis
"""

from typing import Dict, Any


# ============================================================================
# SYSTEM PROMPT
# ============================================================================

CONTENT_AGENT_SYSTEM_PROMPT = """You are an expert Content Generation Agent specialized in creating comprehensive, accurate, and engaging presentation content with a focus on financial analysis.

Your primary responsibilities:
1. Expand outline bullet points into full, detailed content
2. Extract and integrate precise data from RAG retrieval system
3. Ensure 95%+ financial accuracy with proper citations
4. Generate complete visual element specifications for chart generation
5. Create informative speaker notes for each slide
6. Maintain narrative coherence across all slides

Key Capabilities:
- Financial analysis and insight generation
- Data extraction and synthesis from multiple sources
- Numeric consistency and calculation verification
- Professional business writing with appropriate tone
- Citation management and source attribution

Quality Standards:
- Target Response Time: <4 seconds
- Financial Accuracy: 95%+
- All data claims must be backed by RAG-retrieved context
- Citations required for all financial figures
- Clear, concise, and actionable content

Available Tools:
1. query_rag_system: Query the RAG endpoint for specific information
2. format_financial_data: Format financial data with proper units and precision
3. generate_visual_specs: Create complete specifications for visual elements
4. verify_data_consistency: Verify consistency of financial data across slides

Process:
1. Analyze the outline and identify data requirements
2. Query RAG system strategically for needed information
3. Expand each bullet point with detailed, accurate content
4. Add data mappings with actual values from RAG
5. Create complete visual element specifications
6. Generate comprehensive speaker notes
7. Verify accuracy and narrative flow

Remember: You are creating content for {target_audience} with a {tone} tone. Focus on {key_themes}."""


# ============================================================================
# RAG QUERY PROMPT TEMPLATE
# ============================================================================

RAG_QUERY_GENERATION_PROMPT = """Based on the following bullet point and context, generate an optimized RAG query to retrieve the specific information needed.

Bullet Point: {bullet_text}
Requires Data: {requires_data}
Data Mapping: {data_mapping}
Presentation Context: {presentation_context}

Time Periods: {time_periods}
Metrics Needed: {metrics}
Data Categories: {data_categories}

Generate a focused query that will retrieve:
- Specific numerical data
- Relevant context and explanations
- Comparative information if needed
- Source attribution

Also recommend:
- RAG Mode (hybrid/naive/local/global): Choose based on query type
  * hybrid: For multi-faceted queries needing both specific and contextual data
  * local: For specific metric lookups within known documents
  * global: For broad thematic queries across all documents
  * naive: For simple keyword-based retrieval
- top_k value (1-20): Number of results needed
- System prompt customization if needed

Output format:
{{
  "query": "your optimized query string",
  "mode": "recommended mode",
  "top_k": recommended_number,
  "reasoning": "why you chose these parameters"
}}"""


# ============================================================================
# CONTENT EXPANSION PROMPT
# ============================================================================

CONTENT_EXPANSION_PROMPT = """Expand the following bullet point into comprehensive, professional presentation content.

Original Bullet: {bullet_text}
Sub-bullets: {sub_bullets}
Slide Context: {slide_context}
Key Message: {key_message}

RAG Retrieved Data:
{rag_data}

Requirements:
- Detail Level: {detail_level}
- Include Financial Data: {include_financial_data}
- Add Citations: {add_citations}
- Tone: {tone}

Instructions:
1. Expand the bullet into 2-4 complete sentences
2. Integrate specific data from RAG retrieval with proper formatting
3. Use professional financial terminology appropriate for {target_audience}
4. Add citations in [Source: Document Name] format
5. Ensure numerical accuracy and consistency
6. Make content actionable and insightful

If this bullet requires data (requiresData=true):
- Include specific metrics with values
- Add context around the numbers
- Explain significance or trends
- Compare values if applicable

Output the expanded content as clear, professional text suitable for a presentation slide."""


# ============================================================================
# VISUAL ELEMENT SPECIFICATION PROMPT
# ============================================================================

VISUAL_ELEMENT_SPECIFICATION_PROMPT = """Create complete specifications for a visual element based on the outline hint and retrieved data.

Visual Hint from Outline:
- Visual Type: {visual_type}
- Chart Type: {chart_type}
- Data Source: {data_source}
- Purpose: {purpose}

Retrieved Data:
{rag_data}

Slide Context:
- Slide Title: {slide_title}
- Key Message: {key_message}
- Bullet Points: {bullet_context}

User Visual Preferences:
- Preferred Chart Types: {preferred_charts}
- Color Scheme: {color_scheme}
- Style: {style}

Generate a COMPLETE visual element specification that includes:

1. visualType: Type of visual (chart/image/diagram)
2. chartType: Specific chart type (line_chart, bar_chart, candlestick_chart, pie_chart, area_chart, scatter_plot, etc.)
3. dataSource: Source document or metric name
4. dataValue: Brief description of what data represents
5. purpose: Clear purpose statement
6. xAxisLabel: Label for X-axis (for charts)
7. yAxisLabel: Label for Y-axis (for charts)
8. title: Chart title
9. dataPoints: Array of data points in format [{{"x": value, "y": value, "label": label}}]
10. colorScheme: Color scheme from preferences
11. annotations: List of important annotations/callouts

CRITICAL: The dataPoints array must contain the actual numerical data extracted from RAG in a format ready for plotting. Parse all relevant numbers from the RAG data.

Example output structure:
{{
  "visualType": "chart",
  "chartType": "line_chart",
  "dataSource": "BDX Stock Historical Data",
  "dataValue": "Daily closing prices for August-September 2025",
  "purpose": "Show price trend over time period",
  "xAxisLabel": "Date",
  "yAxisLabel": "Price (USD)",
  "title": "BDX Stock Price Trend: Aug-Sep 2025",
  "dataPoints": [
    {{"x": "2025-08-01", "y": 245.32, "label": "Aug 1"}},
    {{"x": "2025-08-15", "y": 248.67, "label": "Aug 15"}},
    ...
  ],
  "colorScheme": "Corporate blue and green",
  "annotations": ["Peak on Aug 15", "Dip on Sep 5"]
}}

Ensure all fields are populated with specific, actionable information."""


# ============================================================================
# SPEAKER NOTES GENERATION PROMPT
# ============================================================================

SPEAKER_NOTES_PROMPT = """Generate comprehensive speaker notes for this slide.

Slide Information:
- Slide Number: {slide_number}
- Title: {slide_title}
- Type: {slide_type}
- Key Message: {key_message}

Expanded Content:
{bullet_points_content}

Visual Elements:
{visual_elements}

Context:
- Target Audience: {target_audience}
- Presentation Objectives: {objectives}

Generate speaker notes that:
1. Explain the key message in detail (2-3 sentences)
2. Provide context for the data presented
3. Highlight important insights or trends
4. Suggest talking points and emphasis areas
5. Include transition hints to next slide
6. Note any caveats or limitations

Speaker notes should be conversational yet professional, helping the presenter deliver maximum impact.

Length: 100-200 words per slide."""


# ============================================================================
# DATA VERIFICATION PROMPT
# ============================================================================

DATA_VERIFICATION_PROMPT = """Verify the accuracy and consistency of financial data across the presentation content.

Slides to Verify:
{slides_content}

Verification Checks:
1. Numerical Accuracy: All figures match RAG sources
2. Unit Consistency: USD, percentages, millions properly formatted
3. Calculation Verification: Any derived metrics are correct
4. Cross-slide Consistency: Same metrics have same values across slides
5. Citation Completeness: All data has source attribution
6. Contextual Accuracy: Data interpretation is sound

For each issue found, provide:
- Slide number
- Data element with issue
- Issue description
- Correct value (if applicable)
- Severity (high/medium/low)

Output format:
{{
  "verification_passed": true/false,
  "accuracy_score": 0.0-1.0,
  "issues": [
    {{
      "slide_number": X,
      "element": "description",
      "issue": "description",
      "correct_value": "value",
      "severity": "high/medium/low"
    }}
  ],
  "recommendations": ["list of improvements"]
}}"""


# ============================================================================
# NARRATIVE COHERENCE PROMPT
# ============================================================================

NARRATIVE_COHERENCE_PROMPT = """Evaluate and ensure narrative coherence across all slides.

Presentation Content:
{presentation_content}

Key Themes: {key_themes}
Objectives: {objectives}

Evaluate:
1. Logical Flow: Does each slide build on the previous?
2. Theme Consistency: Are key themes woven throughout?
3. Progression: Is there clear beginning, middle, end?
4. Transitions: Are connections between slides clear?
5. Message Alignment: Does content support objectives?

Provide:
1. Coherence Score (0.0-1.0)
2. Flow Analysis per slide
3. Suggested improvements
4. Transition recommendations

Output format:
{{
  "coherence_score": 0.0-1.0,
  "flow_analysis": [
    {{
      "slide_number": X,
      "connection_quality": "strong/adequate/weak",
      "notes": "analysis"
    }}
  ],
  "improvements": ["suggestions"],
  "transition_recommendations": ["recommendations"]
}}"""


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with provided kwargs"""
    return template.format(**kwargs)


def get_rag_query_prompt(
    bullet_text: str,
    requires_data: bool,
    data_mapping: Dict[str, Any],
    presentation_context: str,
    time_periods: list,
    metrics: list,
    data_categories: list
) -> str:
    """Generate RAG query prompt"""
    return format_prompt(
        RAG_QUERY_GENERATION_PROMPT,
        bullet_text=bullet_text,
        requires_data=requires_data,
        data_mapping=data_mapping,
        presentation_context=presentation_context,
        time_periods=time_periods,
        metrics=metrics,
        data_categories=data_categories
    )


def get_content_expansion_prompt(
    bullet_text: str,
    sub_bullets: list,
    slide_context: str,
    key_message: str,
    rag_data: str,
    detail_level: str,
    include_financial_data: bool,
    add_citations: bool,
    tone: str,
    target_audience: str
) -> str:
    """Generate content expansion prompt"""
    return format_prompt(
        CONTENT_EXPANSION_PROMPT,
        bullet_text=bullet_text,
        sub_bullets=sub_bullets,
        slide_context=slide_context,
        key_message=key_message,
        rag_data=rag_data,
        detail_level=detail_level,
        include_financial_data=include_financial_data,
        add_citations=add_citations,
        tone=tone,
        target_audience=target_audience
    )


def get_visual_specification_prompt(
    visual_type: str,
    chart_type: str,
    data_source: str,
    purpose: str,
    rag_data: str,
    slide_title: str,
    key_message: str,
    bullet_context: str,
    preferred_charts: list,
    color_scheme: str,
    style: str
) -> str:
    """Generate visual element specification prompt"""
    return format_prompt(
        VISUAL_ELEMENT_SPECIFICATION_PROMPT,
        visual_type=visual_type,
        chart_type=chart_type,
        data_source=data_source,
        purpose=purpose,
        rag_data=rag_data,
        slide_title=slide_title,
        key_message=key_message,
        bullet_context=bullet_context,
        preferred_charts=preferred_charts,
        color_scheme=color_scheme,
        style=style
    )


def get_speaker_notes_prompt(
    slide_number: int,
    slide_title: str,
    slide_type: str,
    key_message: str,
    bullet_points_content: str,
    visual_elements: str,
    target_audience: str,
    objectives: str
) -> str:
    """Generate speaker notes prompt"""
    return format_prompt(
        SPEAKER_NOTES_PROMPT,
        slide_number=slide_number,
        slide_title=slide_title,
        slide_type=slide_type,
        key_message=key_message,
        bullet_points_content=bullet_points_content,
        visual_elements=visual_elements,
        target_audience=target_audience,
        objectives=objectives
    )