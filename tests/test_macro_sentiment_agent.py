import pytest
from src.agents.macro_sentiment_agent import MacroSentimentAgent
from src.models.schemas import MarketRegimeType


def test_macro_sentiment_agent_execution():
    agent = MacroSentimentAgent()
    macro, sentiment, news = agent.run("MSFT", price_trend_signal="STRONG_BULLISH")

    assert macro.fed_funds_rate > 0
    assert macro.yield_10y > 0
    assert macro.yield_2y > 0
    assert macro.vix_level > 0
    assert isinstance(macro.macro_regime, MarketRegimeType)

    assert -1.0 <= sentiment.aggregate_score <= 1.0
    assert sentiment.overall_sentiment in ["BULLISH", "MODERATELY_BULLISH", "NEUTRAL", "BEARISH"]
    assert sentiment.bullish_mentions >= 0
    assert sentiment.bearish_mentions >= 0
    assert len(news) > 0
