import pytest
import pandas as pd
from src.indicators.fibonacci import FibonacciRetracementEngine


def test_fibonacci_uptrend_levels():
    prices = list(range(100, 201, 2))
    engine = FibonacciRetracementEngine(lookback_window=len(prices))
    dates = pd.date_range("2025-01-01", periods=len(prices), freq="B")
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": prices,
            "Low": prices,
            "Close": prices,
            "Volume": [1000] * len(prices),
        },
        index=dates,
    )

    fibo = engine.compute_levels(df)

    assert fibo.swing_high == 200.0
    assert fibo.swing_low == 100.0
    assert fibo.trend_direction == "UPTREND"
    assert fibo.level_0 == 200.0
    assert fibo.level_500 == 150.0  # 50% retracement
    assert fibo.level_100 == 100.0
    assert fibo.level_618 == round(200.0 - 0.618 * 100.0, 2)
    assert fibo.nearest_support <= fibo.swing_high
