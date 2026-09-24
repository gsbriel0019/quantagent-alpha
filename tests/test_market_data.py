import pytest
import pandas as pd
from src.data.market_data import MarketDataLoader


def test_market_data_synthetic_fallback(tmp_path):
    loader = MarketDataLoader(cache_dir=str(tmp_path))
    df = loader._generate_synthetic_ohlcv("TEST", period="1y")

    assert not df.empty
    assert len(df) == 252
    assert "Open" in df.columns
    assert "High" in df.columns
    assert "Low" in df.columns
    assert "Close" in df.columns
    assert "Volume" in df.columns

    # Check high >= low
    assert (df["High"] >= df["Low"]).all()


def test_market_data_fetch_pair(tmp_path):
    loader = MarketDataLoader(cache_dir=str(tmp_path))
    asset_df, bench_df = loader.fetch_pair_data("AAPL", benchmark="^GSPC", period="6mo")

    assert not asset_df.empty
    assert not bench_df.empty
    assert len(asset_df) >= 30
    assert len(bench_df) >= 30
