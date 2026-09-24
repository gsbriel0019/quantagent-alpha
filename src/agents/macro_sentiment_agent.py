import numpy as np
from typing import Tuple, List
from src.agents.base import BaseAgent
from src.models.schemas import MacroRegime, MarketRegimeType, SentimentAnalysis, NewsSentimentItem
from src.data.macro_data import MacroDataLoader


class MacroSentimentAgent(BaseAgent):
    """Institutional Macroeconomic Environment and Financial News Sentiment Agent."""

    def __init__(self):
        super().__init__(
            name="MacroSentimentAgent",
            role="Macro Regime Classification, Rates Analysis & NLP News Sentiment"
        )
        self.data_loader = MacroDataLoader()

    def run(
        self,
        ticker: str,
        price_trend_signal: str
    ) -> Tuple[MacroRegime, SentimentAnalysis, List[NewsSentimentItem]]:
        """Evaluates macro regime and NLP sentiment indicators."""
        clean_ticker = ticker.strip().upper()

        # Ingest live or calibrated macro indicators
        macro_raw = self.data_loader.fetch_live_macro_indicators()
        news_raw = self.data_loader.fetch_curated_news_sentiment(clean_ticker)

        vix = macro_raw["vix_level"]
        spread = macro_raw["yield_curve_spread"]
        is_inverted = macro_raw["is_yield_curve_inverted"]
        fed_rate = macro_raw["fed_funds_rate"]
        inflation = macro_raw["us_cpi_inflation"]
        y10 = macro_raw["yield_10y"]
        y2 = macro_raw["yield_2y"]

        # VIX Regime Classification
        if vix < 15.0:
            vix_regime = "LOW_VOLATILITY_COMPLACENCY"
        elif vix <= 22.0:
            vix_regime = "NORMAL_VOLATILITY"
        elif vix <= 30.0:
            vix_regime = "ELEVATED_VOLATILITY_HEDGING"
        else:
            vix_regime = "HIGH_VOLATILITY_PANIC"

        # Macro Regime Classification
        tailwinds = []
        headwinds = []

        if is_inverted and vix >= 20.0:
            regime = MarketRegimeType.CONTRACTION_RISK_OFF
            headwinds.append("Yield curve inversion and elevated VIX indicate contractionary risk-off pressure.")
        elif vix < 17.0 and spread >= 0.0:
            regime = MarketRegimeType.EXPANSION_RISK_ON
            tailwinds.append("Low equity market volatility regime (VIX < 17) favors growth and beta expansion.")
            tailwinds.append("Normalizing yield curve slope supports credit and financial liquidity.")
        elif fed_rate >= 0.05:
            regime = MarketRegimeType.LATE_CYCLE
            headwinds.append("Elevated central bank policy rates (+5.0%) exert valuation compression on multiple expansion.")
            tailwinds.append("Disinflation trend provides potential terminal rate pause window.")
        else:
            regime = MarketRegimeType.RECOVERY
            tailwinds.append("Economic cycle indicators entering cyclical recovery phase.")

        macro_regime_model = MacroRegime(
            fed_funds_rate=round(fed_rate, 4),
            us_cpi_inflation=round(inflation, 4),
            yield_10y=round(y10, 4),
            yield_2y=round(y2, 4),
            yield_curve_spread=round(spread, 4),
            is_yield_curve_inverted=is_inverted,
            vix_level=round(vix, 2),
            vix_regime=vix_regime,
            macro_regime=regime,
            macro_tailwinds=tailwinds,
            macro_headwinds=headwinds,
        )

        # Process News Sentiment Items
        sentiment_items = [
            NewsSentimentItem(
                title=item["title"],
                source=item["source"],
                sentiment_score=round(item["sentiment_score"], 2),
                sentiment_label=item["sentiment_label"],
                relevance=round(item["relevance"], 2),
            )
            for item in news_raw
        ]

        # Aggregate Sentiment Calculation
        if sentiment_items:
            scores = [item.sentiment_score for item in sentiment_items]
            avg_score = float(np.mean(scores))
            bull_cnt = sum(1 for item in sentiment_items if item.sentiment_label == "BULLISH")
            bear_cnt = sum(1 for item in sentiment_items if item.sentiment_label == "BEARISH")
            neut_cnt = sum(1 for item in sentiment_items if item.sentiment_label == "NEUTRAL")
        else:
            avg_score = 0.1
            bull_cnt, bear_cnt, neut_cnt = 1, 0, 1

        if avg_score >= 0.30:
            overall_sentiment = "BULLISH"
        elif avg_score >= 0.05:
            overall_sentiment = "MODERATELY_BULLISH"
        elif avg_score >= -0.15:
            overall_sentiment = "NEUTRAL"
        else:
            overall_sentiment = "BEARISH"

        # Sentiment vs Price Trend Divergence
        is_price_bearish = "BEARISH" in price_trend_signal
        is_price_bullish = "BULLISH" in price_trend_signal

        if is_price_bearish and avg_score > 0.25:
            divergence = "BULLISH_DIVERGENCE"
        elif is_price_bullish and avg_score < -0.20:
            divergence = "BEARISH_DIVERGENCE"
        else:
            divergence = "CONVERGENT"

        sentiment_model = SentimentAnalysis(
            aggregate_score=round(avg_score, 2),
            overall_sentiment=overall_sentiment,
            bullish_mentions=bull_cnt,
            bearish_mentions=bear_cnt,
            neutral_mentions=neut_cnt,
            key_themes=[
                "Enterprise Growth & AI Monetization",
                "Operating Margin Resiliency",
                "Macro Yield Sensitivity"
            ],
            sentiment_price_divergence=divergence,
        )

        return macro_regime_model, sentiment_model, sentiment_items
