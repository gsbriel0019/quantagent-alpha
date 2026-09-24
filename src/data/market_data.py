import logging
import os
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class MarketDataLoader:
    """Institutional Market Data Loader with caching and offline simulation fallback."""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_ohlcv(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        use_cache: bool = True
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data for an equity or ETF."""
        clean_ticker = ticker.strip().upper()
        cache_file = self.cache_dir / f"{clean_ticker}_{period}_{interval}.parquet"

        if use_cache and cache_file.exists():
            try:
                df = pd.read_parquet(cache_file)
                if not df.empty and len(df) > 30:
                    logger.info(f"Loaded {clean_ticker} from cache ({len(df)} rows)")
                    return df
            except Exception as e:
                logger.warning(f"Failed to read cache for {clean_ticker}: {e}")

        # Fetch from Yahoo Finance
        try:
            logger.info(f"Fetching {clean_ticker} from Yahoo Finance...")
            data = yf.download(clean_ticker, period=period, interval=interval, progress=False)

            if isinstance(data.columns, pd.MultiIndex):
                # Flatten multi-index columns if returned by yfinance
                data.columns = [col[0] for col in data.columns]

            if not data.empty and len(data) >= 30:
                data = data.dropna(subset=["Close"])
                # Standardize column names
                data.columns = [c.capitalize() for c in data.columns]
                # Save cache
                try:
                    data.to_parquet(cache_file)
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")
                return data
            else:
                logger.warning(f"Yahoo Finance returned empty/insufficient data for {clean_ticker}. Using high-fidelity synthetic fallback.")
                return self._generate_synthetic_ohlcv(clean_ticker, period)
        except Exception as ex:
            logger.warning(f"Error fetching {clean_ticker} via yfinance: {ex}. Falling back to synthetic simulation.")
            return self._generate_synthetic_ohlcv(clean_ticker, period)

    def fetch_pair_data(
        self,
        ticker: str,
        benchmark: str = "^GSPC",
        period: str = "1y"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch asset data alongside market benchmark (e.g. S&P 500)."""
        asset_df = self.fetch_ohlcv(ticker, period=period)
        bench_df = self.fetch_ohlcv(benchmark, period=period)
        return asset_df, bench_df

    def _generate_synthetic_ohlcv(self, ticker: str, period: str) -> pd.DataFrame:
        """Generates realistic geometric Brownian motion price series for testing or offline usage."""
        n_days = 252 if period == "1y" else (126 if period == "6mo" else (504 if period == "2y" else 756))
        np.random.seed(abs(hash(ticker)) % (2**32))

        dates = pd.date_range(end=pd.Timestamp.today(), periods=n_days, freq="B")
        mu = 0.12 / 252  # 12% annual drift
        sigma = 0.28 / np.sqrt(252)  # 28% annual volatility

        base_price = 150.0 if ticker != "^GSPC" else 5000.0
        shocks = np.random.normal(mu, sigma, n_days)
        price_series = base_price * np.exp(np.cumsum(shocks))

        # Build realistic OHLCV bars
        daily_spread = price_series * np.random.uniform(0.008, 0.025, n_days)
        highs = price_series + daily_spread * np.random.uniform(0.4, 0.9, n_days)
        lows = np.maximum(price_series - daily_spread * np.random.uniform(0.4, 0.9, n_days), price_series * 0.5)
        opens = price_series + (np.random.uniform(-0.5, 0.5, n_days) * daily_spread)
        volumes = np.random.lognormal(mean=16.5, sigma=0.5, size=n_days).astype(int)

        df = pd.DataFrame(
            {
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": price_series,
                "Volume": volumes,
            },
            index=dates
        )
        df.index.name = "Date"
        return df
