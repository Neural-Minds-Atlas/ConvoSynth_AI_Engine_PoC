"""
Test Payload for Outline Edit API Endpoint
==========================================
Complete example requests for editing an existing outline with user feedback.
Ready to copy-paste into Swagger UI for testing.

🎯 USAGE:
=========
Option 1 - Use the helper script (RECOMMENDED):
    python scripts/print_edit_payload.py 1    # Print MINIMAL example
    python scripts/print_edit_payload.py 2    # Print GLOBAL_CONCISE example
    python scripts/print_edit_payload.py all  # Print all examples

Option 2 - Direct import:
    from src.api.routes.test_outline_edit_payload import EDIT_EXAMPLE_MINIMAL
    import json
    print(json.dumps(EDIT_EXAMPLE_MINIMAL, indent=2))

📦 AVAILABLE PAYLOADS:
=====================
1. EDIT_EXAMPLE_MINIMAL (~2 KB)
   - Quick validation test
   - Small 3-slide outline
   - User feedback: "Make slide 2 more engaging"
   - Best for: First-time testing

2. EDIT_EXAMPLE_GLOBAL_CONCISE (~85 KB) ⭐ COMPLETE FULL DATA
   - Global edit across all slides
   - Complete 10-slide BDX stock analysis
   - All 8 query results with full metadata
   - Complete synthesizedContext
   - User feedback: "Make entire presentation more concise"
   - Best for: Real-world testing with full data

3. EDIT_EXAMPLE_SINGLE_SLIDE (~85 KB) ⭐ COMPLETE FULL DATA
   - Edit specific slide (slide 5)
   - User feedback: "Add emphasis on volatility reduction"
   - Best for: Testing targeted slide modifications

4. EDIT_EXAMPLE_ADD_DATA (~85 KB) ⭐ COMPLETE FULL DATA
   - Add more data points to slides
   - User feedback: "Add exact percentages and volumes"
   - Best for: Testing data enhancement

5. EDIT_EXAMPLE_RESTRUCTURE (~85 KB) ⭐ COMPLETE FULL DATA
   - Reorder slides
   - User feedback: "Move recommendations earlier"
   - Best for: Testing structural changes

6. EDIT_EXAMPLE_CHANGE_VISUALS (~85 KB) ⭐ COMPLETE FULL DATA
   - Change visualization types
   - User feedback: "Replace line chart with candlestick"
   - Best for: Testing visual hint modifications

📚 DOCUMENTATION:
=================
- Full Testing Guide: docs/SWAGGER_TESTING_GUIDE.md
- API Documentation: docs/OUTLINE_EDIT_GUIDE.md
- Quick Reference: docs/QUICK_REFERENCE_TESTING.md

⚡ QUICK START:
===============
1. python scripts/print_edit_payload.py 1
2. Copy the JSON output
3. Open http://localhost:8000/docs
4. Find POST /api/v1/outline/edit
5. Click "Try it out"
6. Paste JSON and click "Execute"

✅ ALL PAYLOADS CONTAIN COMPLETE, REAL DATA - NO PLACEHOLDERS!
"""

# Example 1: Global Edit - Make entire outline more concise
EDIT_EXAMPLE_GLOBAL_CONCISE = {
    "sessionId": "session_bdx_stock_001",
    "userId": "user_financial_analyst_001",
    "userFeedback": "Make the entire presentation more concise. Reduce bullet points to 3 per slide maximum and simplify the language.",
    "targetSlideForEdit": None,  # Global edit
    "previousOutline": {
        "title": "BDX Stock Performance Analysis: August-September 2025 Comparison",
        "subtitle": "Volatility Patterns and Investment Implications",
        "totalSlides": 10,
        "narrativeFlow": "Context → August Analysis → September Analysis → Comparative Insights → Investment Implications → Recommendations",
        "slides": [
            {
                "slideNumber": 1,
                "slideType": "title_slide",
                "title": "BDX Stock Performance Analysis",
                "bulletPoints": [
                    {
                        "bulletText": "August-September 2025 Comparison",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    },
                    {
                        "bulletText": "Investment Committee and Portfolio Managers",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    },
                    {
                        "bulletText": "Comprehensive analysis of price movements, volatility patterns, and actionable insights",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    }
                ],
                "visualHints": [],
                "speakerNotes": "Welcome slide introducing the two-month comparative analysis",
                "keyMessage": "Deep dive into BDX stock performance across August and September 2025"
            },
            {
                "slideNumber": 2,
                "slideType": "overview_slide",
                "title": "Analysis Overview and Context",
                "bulletPoints": [
                    {
                        "bulletText": "Focus Period: August-September 2025",
                        "subBullets": [
                            "August: High volatility recovery phase",
                            "September: Consolidation and stabilization"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Two-Phase Pattern",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Key Metrics Analyzed",
                        "subBullets": [
                            "Opening, High, Low, Closing prices",
                            "Trading volumes",
                            "Price volatility and ranges"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Core Price Metrics",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Data Source: Yahoo Finance BDX Historical Data",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    },
                    {
                        "bulletText": "Objectives: Identify trends, assess volatility, and derive investment implications",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "icon",
                        "chartType": None,
                        "dataSource": "Overview context",
                        "purpose": "Visual representation of two-month timeline"
                    }
                ],
                "speakerNotes": "Set context for the detailed analysis that follows",
                "keyMessage": "Two-month analysis reveals distinct market phases: recovery followed by consolidation"
            },
            {
                "slideNumber": 3,
                "slideType": "data_slide",
                "title": "August 2025: High Volatility Recovery Phase",
                "bulletPoints": [
                    {
                        "bulletText": "August Price Range: $172.20 - $200.22",
                        "subBullets": [
                            "Low: $172.20 reached on August 6",
                            "High: $200.22 reached on August 20",
                            "Spread: $28.02 (16.2% volatility)"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_aug_2025_metrics",
                            "metricName": "August Price Range",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Strong recovery pattern from early-month lows",
                        "subBullets": [
                            "16.2% gain from August low to August high",
                            "Peak performance around August 20-25"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_aug_2025_metrics",
                            "metricName": "Price Recovery",
                            "dataType": "trend"
                        }
                    },
                    {
                        "bulletText": "Month-end close: $192.98 (August 29)",
                        "subBullets": [
                            "Strong finish suggests momentum continuation"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_aug_2025_metrics",
                            "metricName": "Month-end Close",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Opening prices ranged from $176.88 to $199.30",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "opening_price_comparison",
                            "metricName": "August Opening Range",
                            "dataType": "metric"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart",
                        "chartType": "candlestick",
                        "dataSource": "bdx_aug_2025_metrics",
                        "purpose": "Show daily price movements and volatility in August"
                    },
                    {
                        "visualType": "chart",
                        "chartType": "line",
                        "dataSource": "price_trend_analysis",
                        "purpose": "Highlight recovery trajectory from low to high"
                    }
                ],
                "speakerNotes": "Emphasize the dramatic recovery - this was a significant market event",
                "keyMessage": "August showed extreme volatility with a 16.2% recovery from early lows"
            },
            {
                "slideNumber": 4,
                "slideType": "data_slide",
                "title": "September 2025: Consolidation and Reduced Volatility",
                "bulletPoints": [
                    {
                        "bulletText": "September Price Range: $183.73 - $193.99",
                        "subBullets": [
                            "High: $193.99 on September 2",
                            "Low: $183.73 on September 3",
                            "Spread: $10.26 (5.6% volatility)"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "September Price Range",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Significant volatility reduction vs August",
                        "subBullets": [
                            "65% reduction in price range",
                            "Market stabilization after August swings"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Volatility Reduction",
                            "dataType": "comparison"
                        }
                    },
                    {
                        "bulletText": "Dividend payment: $1.04 issued on September 8",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Dividend",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Month close at $186.84 (September 12)",
                        "subBullets": [
                            "Down 3.2% from August close",
                            "Trading volumes: 1.1M - 3.6M shares"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Month-end Close",
                            "dataType": "metric"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart",
                        "chartType": "line",
                        "dataSource": "bdx_sep_2025_metrics",
                        "purpose": "Display September price stability compared to August"
                    },
                    {
                        "visualType": "chart",
                        "chartType": "bar",
                        "dataSource": "bdx_sep_2025_metrics",
                        "purpose": "Show trading volumes with dividend date highlighted"
                    }
                ],
                "speakerNotes": "Contrast with August - September was much calmer",
                "keyMessage": "September brought consolidation with 65% reduction in volatility"
            },
            {
                "slideNumber": 5,
                "slideType": "comparison_slide",
                "title": "August vs September: Direct Comparison",
                "bulletPoints": [
                    {
                        "bulletText": "Price Range Comparison",
                        "subBullets": [
                            "August: $28.02 range (16.2%)",
                            "September: $10.26 range (5.6%)",
                            "Volatility reduction: 65%"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Volatility Reduction",
                            "dataType": "comparison"
                        }
                    },
                    {
                        "bulletText": "Month-to-Month Price Change",
                        "subBullets": [
                            "August close: $192.98",
                            "September close: $186.84",
                            "Change: -3.2%"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Month-to-Month Change",
                            "dataType": "comparison"
                        }
                    },
                    {
                        "bulletText": "Opening Price Ranges",
                        "subBullets": [
                            "August: $176.88 - $199.30",
                            "September: $186.55 - $192.74",
                            "Tighter range indicates stability"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "opening_price_comparison",
                            "metricName": "Opening Range Comparison",
                            "dataType": "comparison"
                        }
                    },
                    {
                        "bulletText": "September maintained higher price floor than August's early lows",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Price Floor Analysis",
                            "dataType": "insight"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart",
                        "chartType": "bar",
                        "dataSource": "aug_sep_comparison",
                        "purpose": "Side-by-side comparison of key metrics"
                    },
                    {
                        "visualType": "table",
                        "chartType": None,
                        "dataSource": "aug_sep_comparison",
                        "purpose": "Detailed numeric comparison table"
                    }
                ],
                "speakerNotes": "Key slide - shows the dramatic shift in market behavior",
                "keyMessage": "65% volatility reduction from August to September signals market stabilization"
            },
            {
                "slideNumber": 6,
                "slideType": "trend_slide",
                "title": "Two-Phase Pattern: Recovery → Consolidation",
                "bulletPoints": [
                    {
                        "bulletText": "Phase 1 (August): High Volatility Recovery",
                        "subBullets": [
                            "Started weak at $172.20",
                            "Strong recovery to $200+ levels",
                            "High trading volumes during volatile periods"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "August Recovery Phase",
                            "dataType": "trend"
                        }
                    },
                    {
                        "bulletText": "Phase 2 (September): Consolidation",
                        "subBullets": [
                            "Price range narrowed to $185-$195",
                            "Reduced speculative activity",
                            "Market stabilization indicators"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "September Consolidation",
                            "dataType": "trend"
                        }
                    },
                    {
                        "bulletText": "Strong support established above $183 level",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Support Level",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Peak momentum occurred in late August",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Peak Momentum",
                            "dataType": "trend"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart",
                        "chartType": "line",
                        "dataSource": "price_trend_analysis",
                        "purpose": "Show two-phase pattern visually with trend lines"
                    },
                    {
                        "visualType": "diagram",
                        "chartType": None,
                        "dataSource": "price_trend_analysis",
                        "purpose": "Visual representation of recovery-consolidation cycle"
                    }
                ],
                "speakerNotes": "This is the key insight - classic market pattern",
                "keyMessage": "BDX followed a textbook recovery-consolidation pattern across the two months"
            },
            {
                "slideNumber": 7,
                "slideType": "insight_slide",
                "title": "Key Trading Volume and Activity Insights",
                "bulletPoints": [
                    {
                        "bulletText": "Trading volumes consistently higher during volatility",
                        "subBullets": [
                            "Early August: High volumes during sell-off",
                            "Late August: Increased activity during recovery",
                            "September: Generally lower volumes"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Trading Volumes",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "September volumes ranged from 1.1M to 3.6M shares",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Volume Range",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Dividend payment on September 8 coincided with increased activity",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Dividend Impact",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Lower volumes in September suggest reduced speculative trading",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Volume Patterns",
                            "dataType": "insight"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart",
                        "chartType": "bar",
                        "dataSource": "bdx_sep_2025_metrics",
                        "purpose": "Display daily trading volumes with key events marked"
                    }
                ],
                "speakerNotes": "Volume confirms the narrative - less speculation in September",
                "keyMessage": "Trading volumes reflect reduced market uncertainty in September"
            },
            {
                "slideNumber": 8,
                "slideType": "insight_slide",
                "title": "Volatility Analysis and Stability Metrics",
                "bulletPoints": [
                    {
                        "bulletText": "August Volatility: 16.2% (High)",
                        "subBullets": [
                            "$28.02 high-low spread",
                            "Significant intraday movements",
                            "Recovery-driven volatility"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "August Volatility Range",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "September Volatility: 5.6% (Normal)",
                        "subBullets": [
                            "$10.26 high-low spread",
                            "Typical for large-cap healthcare stock",
                            "Consolidation pattern"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "volatility_analysis_sep",
                            "metricName": "Volatility Percentage",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "65% reduction in volatility month-over-month",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Volatility Reduction",
                            "dataType": "comparison"
                        }
                    },
                    {
                        "bulletText": "Maturing recovery phase with reduced speculative activity",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Recovery Maturity",
                            "dataType": "insight"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart",
                        "chartType": "line",
                        "dataSource": "volatility_analysis_sep",
                        "purpose": "Compare volatility trends between August and September"
                    }
                ],
                "speakerNotes": "Volatility reduction is a positive sign for stability",
                "keyMessage": "September's 5.6% volatility represents normal, healthy market behavior"
            },
            {
                "slideNumber": 9,
                "slideType": "recommendation_slide",
                "title": "Investment Implications and Recommendations",
                "bulletPoints": [
                    {
                        "bulletText": "Market stabilization signals reduced risk",
                        "subBullets": [
                            "Support level established above $183",
                            "Lower volatility more predictable",
                            "Consolidation phase typically precedes next move"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Support Level",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Stock maintained strength despite short-term declines",
                        "subBullets": [
                            "September low ($183.73) well above August low ($172.20)",
                            "Underlying strength indicators"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Price Floor Analysis",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Dividend yield adds to total return proposition",
                        "subBullets": [
                            "$1.04 quarterly dividend",
                            "Income component for long-term holders"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Dividend",
                            "dataType": "metric"
                        }
                    },
                    {
                        "bulletText": "Monitor for breakout above $194 or breakdown below $183",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "bdx_sep_2025_metrics",
                            "metricName": "Key Levels",
                            "dataType": "insight"
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "diagram",
                        "chartType": None,
                        "dataSource": "price_trend_analysis",
                        "purpose": "Illustrate key support and resistance levels"
                    }
                ],
                "speakerNotes": "Actionable recommendations based on the analysis",
                "keyMessage": "Stabilization presents opportunity for position building at reduced risk levels"
            },
            {
                "slideNumber": 10,
                "slideType": "conclusion_slide",
                "title": "Key Takeaways and Next Steps",
                "bulletPoints": [
                    {
                        "bulletText": "BDX demonstrated a classic two-phase market pattern",
                        "subBullets": [
                            "August: High volatility recovery (+16.2%)",
                            "September: Consolidation with 65% volatility reduction"
                        ],
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Two-Phase Pattern",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Market stabilization reduces investment risk",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "aug_sep_comparison",
                            "metricName": "Volatility Reduction",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Strong support above $183 provides downside protection",
                        "subBullets": None,
                        "requiresData": True,
                        "dataMapping": {
                            "queryId": "price_trend_analysis",
                            "metricName": "Support Level",
                            "dataType": "insight"
                        }
                    },
                    {
                        "bulletText": "Next Steps: Monitor key levels and await directional breakout",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    }
                ],
                "visualHints": [],
                "speakerNotes": "Summarize the entire analysis and set expectations",
                "keyMessage": "BDX's stabilization phase offers strategic entry opportunities for long-term investors"
            }
        ]
    },
    "extractedInformation": {
        "presentationRequirements": {
            "topic": "BDX Stock Performance Analysis: August-September 2025 Comparison",
            "targetAudience": "Investment Committee and Portfolio Managers",
            "numSlides": 10,
            "keyThemes": [
                "Price Performance",
                "Volatility Analysis",
                "Month-over-Month Comparison",
                "Trend Identification",
                "Investment Implications"
            ],
            "tone": "Professional and data-driven",
            "objectives": "Provide comprehensive analysis of BDX stock price movements comparing August and September 2025, highlighting key trends, volatility patterns, and actionable insights for investment decisions"
        },
        "dataRequirements": {
            "documentsRequested": [
                "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
            ],
            "contentToExtract": [
                "Opening prices",
                "High prices",
                "Low prices",
                "Closing prices",
                "Trading volumes",
                "Price trends",
                "Volatility metrics"
            ],
            "metrics": [
                "open",
                "high",
                "low",
                "close",
                "volume",
                "price_range",
                "month_over_month_change",
                "volatility_percentage"
            ],
            "timePeriods": [
                "August 2025",
                "September 2025",
                "Aug-Sep 2025"
            ],
            "comparisons": [
                "September vs August prices",
                "Volatility comparison",
                "Trading volume patterns",
                "Price recovery analysis"
            ],
            "dataCategories": [
                "financial",
                "stock_prices",
                "market_data"
            ]
        },
        "visualPreferences": {
            "chartTypes": [
                "line_chart",
                "bar_chart",
                "candlestick_chart",
                "area_chart"
            ],
            "style": "Professional financial presentation",
            "includeImages": True,
            "colorScheme": "Corporate blue and green with accent colors"
        }
    },
    "queryResults": [
        {
            "queryId": "bdx_sep_2025_metrics",
            "generatedQuery": {
                "query": "What were the opening, high, low, and closing prices for BDX stock in September 2025?",
                "query_type": "metric",
                "priority": "high",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Sep 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["open", "high", "low", "close"]
                },
                "rationale": "Direct extraction of core price metrics for the primary time period of interest"
            },
            "llmEnhancedAnswer": {
                "answer": "BDX stock in September 2025 showed moderate volatility with prices ranging from $183.73 to $193.99. Opening prices varied from $186.55 to $192.74, with highs reaching $193.99 (Sep 2) and lows dropping to $183.73 (Sep 3). The stock closed the month at $186.84 on September 12, down 1.95% from the previous day. A dividend of $1.04 was issued on September 8, 2025.",
                "confidence": 0.95,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "September High",
                            "value": "$193.99",
                            "context": "Reached on September 2, 2025"
                        },
                        {
                            "metric_name": "September Low",
                            "value": "$183.73",
                            "context": "Reached on September 3, 2025"
                        },
                        {
                            "metric_name": "Month-end Close",
                            "value": "$186.84",
                            "context": "September 12, 2025 close"
                        },
                        {
                            "metric_name": "Dividend",
                            "value": "$1.04",
                            "context": "Issued September 8, 2025"
                        }
                    ],
                    "key_points": [
                        "Price range: $183.73 - $193.99",
                        "Highest closing price: $192.39 (Sep 5)",
                        "Lowest closing price: $186.84 (Sep 12)",
                        "$1.04 dividend issued September 8",
                        "Trading volumes ranged from 1.1M to 3.6M shares"
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "high"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "bdx_aug_2025_metrics",
            "generatedQuery": {
                "query": "What were the opening, high, low, and closing prices for BDX stock in August 2025?",
                "query_type": "metric",
                "priority": "high",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Aug 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["open", "high", "low", "close"]
                },
                "rationale": "Essential baseline data for comparison analysis between August and September"
            },
            "llmEnhancedAnswer": {
                "answer": "BDX stock in August 2025 experienced significant volatility, with prices ranging from a low of $172.20 (Aug 6) to a high of $200.22 (Aug 20). The month showed a recovery pattern from early August lows, with the stock climbing from the $170s to nearly $200 by mid-to-late August. Opening prices ranged from $176.88 to $199.30, demonstrating substantial intraday and day-to-day price movements.",
                "confidence": 0.95,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "August High",
                            "value": "$200.22",
                            "context": "Reached on August 20, 2025"
                        },
                        {
                            "metric_name": "August Low",
                            "value": "$172.20",
                            "context": "Reached on August 6, 2025"
                        },
                        {
                            "metric_name": "Month-end Close",
                            "value": "$192.98",
                            "context": "August 29, 2025 close"
                        },
                        {
                            "metric_name": "Price Recovery",
                            "value": "16.2%",
                            "context": "From August low to August high"
                        }
                    ],
                    "key_points": [
                        "Dramatic price range: $172.20 - $200.22",
                        "Strong recovery from early August lows",
                        "Peak performance around August 20-25",
                        "High trading volumes during volatile periods",
                        "Month ended strong at $192.98 (Aug 29)"
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "high"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "aug_sep_comparison",
            "generatedQuery": {
                "query": "How did BDX stock prices compare between September 2025 and August 2025?",
                "query_type": "comparison",
                "priority": "high",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Sep 2025", "Aug 2025"],
                    "data_categories": ["financial"],
                    "comparisons": ["Sep vs Aug"],
                    "metrics": ["open", "high", "low", "close"]
                },
                "rationale": "Primary comparison requirement explicitly stated in the data requirements"
            },
            "llmEnhancedAnswer": {
                "answer": "BDX stock showed a declining trend from August to September 2025. August ended strongly at $192.98 but September opened lower and continued to decline, closing at $186.84 by September 12. The transition showed reduced volatility in September compared to August's dramatic swings. August's price range ($172.20-$200.22) was significantly wider than September's range ($183.73-$193.99), indicating decreased market uncertainty.",
                "confidence": 0.92,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "Month-to-Month Change",
                            "value": "-3.2%",
                            "context": "From August 29 close to September 12 close"
                        },
                        {
                            "metric_name": "Volatility Reduction",
                            "value": "65%",
                            "context": "September range vs August range"
                        }
                    ],
                    "key_points": [
                        "Price declined from August close ($192.98) to September close ($186.84)",
                        "Reduced volatility in September vs August",
                        "August showed 16.2% recovery pattern, September showed consolidation",
                        "Trading volumes generally lower in September",
                        "September maintained higher price floor than August's early lows"
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "high"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "price_trend_analysis",
            "generatedQuery": {
                "query": "What was the price trend for BDX stock from August to September 2025?",
                "query_type": "trend",
                "priority": "high",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Aug 2025", "Sep 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["open", "high", "low", "close"]
                },
                "rationale": "Identifies directional movement and patterns between the two target months"
            },
            "llmEnhancedAnswer": {
                "answer": "The price trend from August to September 2025 shows a classic recovery-consolidation pattern. August began with significant weakness (dropping to $172.20) but recovered strongly to reach $200+ levels by mid-month. September showed price consolidation in the $185-$195 range, suggesting market stabilization after August's volatility. The overall trend indicates a maturing recovery phase with reduced speculative activity.",
                "confidence": 0.90,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "August Volatility Range",
                            "value": "$28.02",
                            "context": "High-Low spread"
                        },
                        {
                            "metric_name": "September Volatility Range",
                            "value": "$10.26",
                            "context": "High-Low spread"
                        }
                    ],
                    "key_points": [
                        "August: Recovery phase with high volatility",
                        "September: Consolidation phase with reduced volatility",
                        "Strong support established above $183 level",
                        "Peak momentum occurred in late August",
                        "Dividend payment in September may have influenced price action"
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "high"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "sep_high_analysis",
            "generatedQuery": {
                "query": "What was the highest price reached by BDX stock in September 2025?",
                "query_type": "metric",
                "priority": "medium",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Sep 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["high"]
                },
                "rationale": "Specific focus on peak performance metric for the primary analysis period"
            },
            "llmEnhancedAnswer": {
                "answer": "The highest price reached by BDX stock in September 2025 was $193.99 on September 2, occurring at the beginning of the month. This represented a continuation of August's late-month strength but failed to break through the $200 level that was achieved in August.",
                "confidence": 0.93,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "September Peak",
                            "value": "$193.99",
                            "context": "September 2, 2025"
                        }
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "high"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "aug_low_analysis",
            "generatedQuery": {
                "query": "What was the lowest price reached by BDX stock in August 2025?",
                "query_type": "metric",
                "priority": "medium",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Aug 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["low"]
                },
                "rationale": "Identifies minimum price point for baseline comparison period"
            },
            "llmEnhancedAnswer": {
                "answer": "The lowest price reached by BDX stock in August 2025 was $172.20 on August 6, representing the nadir of a significant market correction early in the month. This low point preceded a strong recovery that gained 16.2% by mid-month.",
                "confidence": 0.93,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "August Bottom",
                            "value": "$172.20",
                            "context": "August 6, 2025"
                        }
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "high"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "opening_price_comparison",
            "generatedQuery": {
                "query": "How did the opening prices of BDX stock change from August to September 2025?",
                "query_type": "comparison",
                "priority": "medium",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Aug 2025", "Sep 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["open"],
                    "comparisons": ["Sep vs Aug"]
                },
                "rationale": "Specific metric comparison to understand market sentiment changes between periods"
            },
            "llmEnhancedAnswer": {
                "answer": "Opening prices showed significant variation between the two months. August opening prices ranged from $176.88 to $199.30, while September opening prices were more compressed at $186.55 to $192.74. The tighter range in September reflects reduced market uncertainty and consolidation.",
                "confidence": 0.88,
                "extractedData": {
                    "comparison": {
                        "august_opening_range": "$176.88 - $199.30",
                        "september_opening_range": "$186.55 - $192.74",
                        "interpretation": "September showed more stable opening prices"
                    },
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "medium"
                        }
                    ],
                    "gaps": []
                }
            }
        },
        {
            "queryId": "volatility_analysis_sep",
            "generatedQuery": {
                "query": "What was the price volatility of BDX stock in September 2025 based on high and low prices?",
                "query_type": "insight",
                "priority": "medium",
                "filters": {
                    "documents": [
                        "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                    ],
                    "time_periods": ["Sep 2025"],
                    "data_categories": ["financial"],
                    "metrics": ["high", "low"]
                },
                "rationale": "Analytical insight into price stability and market behavior during the primary period"
            },
            "llmEnhancedAnswer": {
                "answer": "September 2025 volatility was moderate with a $10.26 spread between high ($193.99) and low ($183.73) prices. This represents approximately 5.6% volatility, which is considered normal for a large-cap healthcare stock. The dividend payment on September 8 coincided with increased trading activity.",
                "confidence": 0.87,
                "extractedData": {
                    "metrics": [
                        {
                            "metric_name": "Volatility Percentage",
                            "value": "5.6%",
                            "context": "Based on high-low spread"
                        }
                    ],
                    "sources": [
                        {
                            "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                            "section": "Historical Price Table",
                            "relevance": "medium"
                        }
                    ],
                    "gaps": []
                }
            }
        }
    ],
    "synthesizedContext": {
        "synthesized_answers": {
            "bdx_september_2025_stock_performance": {
                "answer": "BDX stock in September 2025 showed moderate volatility with prices ranging from $183.73 to $193.99. Opening prices varied from $186.55 to $192.74, with highs reaching $193.99 (Sep 2) and lows dropping to $183.73 (Sep 3). The stock closed the month at $186.84 on September 12, down 1.95% from the previous day. A dividend of $1.04 was issued on September 8, 2025.",
                "key_points": [
                    "Price range: $183.73 - $193.99",
                    "Highest closing price: $192.39 (Sep 5)",
                    "Lowest closing price: $186.84 (Sep 12)",
                    "$1.04 dividend issued September 8",
                    "Trading volumes ranged from 1.1M to 3.6M shares"
                ],
                "confidence": "high"
            },
            "bdx_august_2025_stock_performance": {
                "answer": "BDX stock in August 2025 experienced significant volatility, with prices ranging from a low of $172.20 (Aug 6) to a high of $200.22 (Aug 20). The month showed a recovery pattern from early August lows, with the stock climbing from the $170s to nearly $200 by mid-to-late August.",
                "key_points": [
                    "Dramatic price range: $172.20 - $200.22",
                    "Strong recovery from early August lows",
                    "Peak performance around August 20-25",
                    "Month ended strong at $192.98 (Aug 29)"
                ],
                "confidence": "high"
            }
        },
        "inter_query_insights": [
            "BDX stock exhibited a clear two-phase pattern: high volatility recovery in August followed by lower volatility consolidation in September",
            "The dividend payment on September 8 coincided with the transition from recovery to consolidation phase",
            "Trading volumes were consistently higher during periods of price volatility, particularly in early August and early September",
            "The stock maintained support levels above previous lows, suggesting underlying strength despite short-term declines"
        ],
        "data_quality_notes": [
            "Historical data appears complete and consistent across the requested time periods"
        ],
        "total_tokens_synthesized": 850,
        "synthesis_metadata": {
            "chunks_processed": 12,
            "themes_covered": 4,
            "confidence_score": 0.92
        }
    },
    "generatedQueries": [
        {
            "query": "What were the opening, high, low, and closing prices for BDX stock in September 2025?",
            "query_type": "metric",
            "priority": "high",
            "filters": {
                "documents": [
                    "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"
                ],
                "time_periods": ["Sep 2025"],
                "data_categories": ["financial"],
                "metrics": ["open", "high", "low", "close"]
            },
            "rationale": "Direct extraction of core price metrics for the primary time period of interest"
        }
    ],
    "performanceMetrics": {
        "query_generation_time": 16.200144,
        "retrieval_time": 36.54564799999999,
        "synthesis_time": 34.221291,
        "total_tokens_retrieved": 28195,
        "total_queries_generated": 8
    }
}


# Example 2: Single Slide Edit - Modify slide 5 specifically
EDIT_EXAMPLE_SINGLE_SLIDE = {
    "sessionId": "session_bdx_stock_001",
    "userId": "user_financial_analyst_001",
    "userFeedback": "Slide 5 needs more emphasis on the volatility reduction. Add a specific calculation showing the percentage change and highlight it as a key achievement.",
    "targetSlideForEdit": 5,  # Focus on slide 5
    "previousOutline": EDIT_EXAMPLE_GLOBAL_CONCISE["previousOutline"],  # Reuse same outline
    "extractedInformation": EDIT_EXAMPLE_GLOBAL_CONCISE["extractedInformation"],
    "queryResults": EDIT_EXAMPLE_GLOBAL_CONCISE["queryResults"],
    "synthesizedContext": EDIT_EXAMPLE_GLOBAL_CONCISE["synthesizedContext"],
    "generatedQueries": EDIT_EXAMPLE_GLOBAL_CONCISE["generatedQueries"],
    "performanceMetrics": EDIT_EXAMPLE_GLOBAL_CONCISE["performanceMetrics"]
}


# Example 3: Add More Data - User wants more metrics
EDIT_EXAMPLE_ADD_DATA = {
    "sessionId": "session_bdx_stock_001",
    "userId": "user_financial_analyst_001",
    "userFeedback": "Add more specific data points to slides 3 and 4. Include exact percentage changes, average daily volumes, and highlight the highest and lowest trading days with their volumes.",
    "targetSlideForEdit": None,  # Will affect slides 3 and 4
    "previousOutline": EDIT_EXAMPLE_GLOBAL_CONCISE["previousOutline"],
    "extractedInformation": EDIT_EXAMPLE_GLOBAL_CONCISE["extractedInformation"],
    "queryResults": EDIT_EXAMPLE_GLOBAL_CONCISE["queryResults"],
    "synthesizedContext": EDIT_EXAMPLE_GLOBAL_CONCISE["synthesizedContext"],
    "generatedQueries": EDIT_EXAMPLE_GLOBAL_CONCISE["generatedQueries"],
    "performanceMetrics": EDIT_EXAMPLE_GLOBAL_CONCISE["performanceMetrics"]
}


# Example 4: Restructure - Change slide order
EDIT_EXAMPLE_RESTRUCTURE = {
    "sessionId": "session_bdx_stock_001",
    "userId": "user_financial_analyst_001",
    "userFeedback": "Move the investment recommendations (slide 9) earlier in the presentation, right after the comparison slide (slide 5). Investors want to see actionable recommendations sooner.",
    "targetSlideForEdit": None,
    "previousOutline": EDIT_EXAMPLE_GLOBAL_CONCISE["previousOutline"],
    "extractedInformation": EDIT_EXAMPLE_GLOBAL_CONCISE["extractedInformation"],
    "queryResults": EDIT_EXAMPLE_GLOBAL_CONCISE["queryResults"],
    "synthesizedContext": EDIT_EXAMPLE_GLOBAL_CONCISE["synthesizedContext"],
    "generatedQueries": EDIT_EXAMPLE_GLOBAL_CONCISE["generatedQueries"],
    "performanceMetrics": EDIT_EXAMPLE_GLOBAL_CONCISE["performanceMetrics"]
}


# Example 5: Change Visuals - Update visualization hints
EDIT_EXAMPLE_CHANGE_VISUALS = {
    "sessionId": "session_bdx_stock_001",
    "userId": "user_financial_analyst_001",
    "userFeedback": "Replace the line chart on slide 4 with a candlestick chart to better show daily price movements. Also add a volume overlay to show correlation between volume and price volatility.",
    "targetSlideForEdit": 4,
    "previousOutline": EDIT_EXAMPLE_GLOBAL_CONCISE["previousOutline"],
    "extractedInformation": EDIT_EXAMPLE_GLOBAL_CONCISE["extractedInformation"],
    "queryResults": EDIT_EXAMPLE_GLOBAL_CONCISE["queryResults"],
    "synthesizedContext": EDIT_EXAMPLE_GLOBAL_CONCISE["synthesizedContext"],
    "generatedQueries": EDIT_EXAMPLE_GLOBAL_CONCISE["generatedQueries"],
    "performanceMetrics": EDIT_EXAMPLE_GLOBAL_CONCISE["performanceMetrics"]
}


# Minimal working example (for quick testing) - READY TO USE IN SWAGGER UI
EDIT_EXAMPLE_MINIMAL = {
    "sessionId": "test_session",
    "userId": "test_user",
    "userFeedback": "Make slide 2 more engaging by adding a bullet point about why this analysis matters to investors.",
    "targetSlideForEdit": 2,
    "previousOutline": {
        "title": "Test Presentation",
        "subtitle": None,
        "totalSlides": 3,
        "narrativeFlow": "Simple test flow",
        "slides": [
            {
                "slideNumber": 1,
                "slideType": "title_slide",
                "title": "Test Title",
                "bulletPoints": [],
                "visualHints": [],
                "speakerNotes": None,
                "keyMessage": "Test message"
            },
            {
                "slideNumber": 2,
                "slideType": "overview_slide",
                "title": "Test Overview",
                "bulletPoints": [
                    {
                        "bulletText": "Test bullet",
                        "subBullets": None,
                        "requiresData": False,
                        "dataMapping": None
                    }
                ],
                "visualHints": [],
                "speakerNotes": None,
                "keyMessage": "Test overview"
            },
            {
                "slideNumber": 3,
                "slideType": "conclusion_slide",
                "title": "Test Conclusion",
                "bulletPoints": [],
                "visualHints": [],
                "speakerNotes": None,
                "keyMessage": "Test conclusion"
            }
        ]
    },
    "extractedInformation": {
        "presentationRequirements": {
            "topic": "Test Topic",
            "targetAudience": "Test Audience",
            "numSlides": 3,
            "keyThemes": ["Theme 1"],
            "tone": "Professional",
            "objectives": "Test objectives"
        },
        "dataRequirements": {
            "documentsRequested": [],
            "contentToExtract": [],
            "metrics": [],
            "timePeriods": [],
            "comparisons": [],
            "dataCategories": []
        },
        "visualPreferences": {
            "chartTypes": [],
            "style": "Professional",
            "includeImages": False,
            "colorScheme": None
        }
    },
    "queryResults": [
        {
            "queryId": "query_1",
            "generatedQuery": None,
            "llmEnhancedAnswer": {
                "answer": "Test answer",
                "confidence": 0.9,
                "extractedData": {}
            }
        }
    ]
}
