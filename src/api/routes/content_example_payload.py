"""Example payload for Content Agent /generate endpoint"""

CONTENT_GENERATE_EXAMPLE = {
    "sessionId": "session_bdx_stock_analysis_001",
    "userId": "user_portfolio_manager_123",
    "extractedInformation": {
        "dataRequirements": {
            "comparisons": ["Sep vs Aug"],
            "contentToExtract": ["historical prices"],
            "dataCategories": ["financial"],
            "documentsRequested": ["Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"],
            "metrics": ["open", "high", "low", "close"],
            "timePeriods": ["August 2025", "September 2025"]
        },
        "presentationRequirements": {
            "keyThemes": ["Stock Performance", "Volatility Analysis", "Investment Insights"],
            "numSlides": 10,
            "objectives": "Provide comprehensive analysis of BDX stock price movements comparing August and September 2025, highlighting key trends, volatility patterns, and actionable insights for investment decisions",
            "targetAudience": "Investment Committee and Portfolio Managers",
            "tone": "Professional",
            "topic": "BDX Stock Performance Analysis: August-September 2025"
        },
        "visualPreferences": {
            "chartTypes": ["candlestick", "line_chart", "bar_chart"],
            "colorScheme": "Corporate",
            "includeImages": True,
            "style": "Professional"
        }
    },
    "outlineAgentOutput": {
        "success": True,
        "sessionId": "session_bdx_stock_analysis_001",
        "userId": "user_portfolio_manager_123",
        "outlineId": "outline_bdx_001",
        "cycleType": "generate",
        "presentationOutline": {
            "title": "BDX Stock Performance Analysis",
            "subtitle": "August-September 2025 Comparison",
            "totalSlides": 10,
            "narrativeFlow": "Introduction → Context → August Analysis → September Analysis → Comparison → Trends → Insights → Recommendations → Conclusions",
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
        "outlineMetadata": {
            "templateCompliance": True,
            "slideCountCompliance": True,
            "narrativeCoherence": 0.95,
            "dataIntegration": {
                "totalDataPoints": 25,
                "queriesReferenced": ["bdx_aug_2025_metrics", "bdx_sep_2025_metrics", "price_trend_analysis"],
                "coverageScore": 0.92
            }
        },
        "qualityChecks": {
            "allSlidesHaveTitles": True,
            "bulletPointsWithinLimit": True,
            "visualHintsProvided": True,
            "dataBackedClaims": True,
            "logicalFlow": True
        },
        "nextAction": "proceed_to_content_generation",
        "handoffToAgent": "content_agent",
        "performanceMetrics": {
            "responseTime": 2.5,
            "agentIterations": 3,
            "toolCallsMade": 8
        },
        "timestamp": "2025-10-30T12:00:00.000Z",
        "error": None
    },
    "ragEndpoint": "http://localhost:8000/api/v1/query"
}
