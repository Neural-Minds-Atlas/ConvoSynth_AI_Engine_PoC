"""
Complete Test Payloads for Outline Agent API Testing
====================================================
Contains COMPLETE realistic test payloads based on actual Query Agent output for BDX stock analysis.
Includes ALL fields: synthesizedContext, inter_query_insights, data_quality_notes, generatedQueries, etc.
"""

import json
from datetime import datetime

# ===================== COMPLETE BDX Stock Analysis Payload with ALL Fields =====================

BDX_STOCK_ANALYSIS_COMPLETE = {
    "sessionId": "session_bdx_stock_001",
    "userId": "user_financial_analyst_001",
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
                "sources": [
                    {
                        "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                        "section": "Historical Price Table",
                        "relevance": "high"
                    }
                ],
                "confidence": "high",
                "gaps": []
            },
            "bdx_august_2025_stock_performance": {
                "answer": "BDX stock in August 2025 experienced significant volatility, with prices ranging from a low of $172.20 (Aug 6) to a high of $200.22 (Aug 20). The month showed a recovery pattern from early August lows, with the stock climbing from the $170s to nearly $200 by mid-to-late August. Opening prices ranged from $176.88 to $199.30, demonstrating substantial intraday and day-to-day price movements.",
                "key_points": [
                    "Dramatic price range: $172.20 - $200.22",
                    "Strong recovery from early August lows",
                    "Peak performance around August 20-25",
                    "High trading volumes during volatile periods",
                    "Month ended strong at $192.98 (Aug 29)"
                ],
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
                "sources": [
                    {
                        "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                        "section": "Historical Price Table",
                        "relevance": "high"
                    }
                ],
                "confidence": "high",
                "gaps": []
            },
            "august_to_september_comparison": {
                "answer": "BDX stock showed a declining trend from August to September 2025. August ended strongly at $192.98 but September opened lower and continued to decline, closing at $186.84 by September 12. The transition showed reduced volatility in September compared to August's dramatic swings. August's price range ($172.20-$200.22) was significantly wider than September's range ($183.73-$193.99), indicating decreased market uncertainty.",
                "key_points": [
                    "Price declined from August close ($192.98) to September close ($186.84)",
                    "Reduced volatility in September vs August",
                    "August showed 16.2% recovery pattern, September showed consolidation",
                    "Trading volumes generally lower in September",
                    "September maintained higher price floor than August's early lows"
                ],
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
                "sources": [
                    {
                        "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                        "section": "Historical Price Table",
                        "relevance": "high"
                    }
                ],
                "confidence": "high",
                "gaps": []
            },
            "price_trend_analysis": {
                "answer": "The price trend from August to September 2025 shows a classic recovery-consolidation pattern. August began with significant weakness (dropping to $172.20) but recovered strongly to reach $200+ levels by mid-month. September showed price consolidation in the $185-$195 range, suggesting market stabilization after August's volatility. The overall trend indicates a maturing recovery phase with reduced speculative activity.",
                "key_points": [
                    "August: Recovery phase with high volatility",
                    "September: Consolidation phase with reduced volatility",
                    "Strong support established above $183 level",
                    "Peak momentum occurred in late August",
                    "Dividend payment in September may have influenced price action"
                ],
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
                "sources": [
                    {
                        "document": "Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf",
                        "section": "Historical Price Table",
                        "relevance": "high"
                    }
                ],
                "confidence": "high",
                "gaps": []
            }
        },
        "inter_query_insights": [
            "BDX stock exhibited a clear two-phase pattern: high volatility recovery in August followed by lower volatility consolidation in September",
            "The dividend payment on September 8 coincided with the transition from recovery to consolidation phase",
            "Trading volumes were consistently higher during periods of price volatility, particularly in early August and early September",
            "The stock maintained support levels above previous lows, suggesting underlying strength despite short-term declines"
        ],
        "data_quality_notes": [
            "Some irrelevant medical report data was included in retrieved chunks but filtered out during synthesis",
            "Historical data appears complete and consistent across the requested time periods",
            "Form 25 document reference suggests some corporate action but doesn't directly impact price analysis"
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
        },
        {
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
        {
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
        {
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
        {
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
        {
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
        {
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
        {
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