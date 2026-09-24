import pytest
import numpy as np
import pandas as pd
from src.indicators.technical import TechnicalAnalysisEngine


@pytest.fixture
def sample_ohlcv():
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    prices = 100.0 * np.exp(np.cumsum(np.random.normal(0.001, 0.015, 100)))
    df = pd.DataFrame(
        {
            "Open": prices * 0.99,
            "High": prices * 1.02,
            "Low": prices * 0.98,
            "Close": prices,
            "Volume": np.random.randint(100000, 500000, 100),
        },
        index=dates,
    )
    return df


def test_technical_indicators_computation(sample_ohlcv):
    engine = TechnicalAnalysisEngine()
    indicators = engine.compute_indicators(sample_ohlcv)

    assert indicators.current_price > 0
    assert indicators.ema_20 > 0
    assert indicators.ema_50 > 0
    assert 0 <= indicators.rsi_14 <= 100
    assert indicators.bollinger_upper >= indicators.bollinger_middle >= indicators.bollinger_lower
    assert indicators.atr_14 > 0
    assert indicators.trend_signal in [
        "STRONG_BULLISH", "MODERATELY_BULLISH", "CONSOLIDATION_NEUTRAL",
        "MODERATELY_BEARISH", "STRONG_BEARISH"
    ]
    assert indicators.rsi_condition in ["OVERBOUGHT", "OVERSOLD", "NEUTRAL"]


def test_insufficient_data_error():
    engine = TechnicalAnalysisEngine()
    short_df = pd.DataFrame({"Close": [10.0, 11.0, 12.0]})
    with pytest.raises(ValueError):
        engine.compute_indicators(short_df)
