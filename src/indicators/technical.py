import numpy as np
import pandas as pd
from src.models.schemas import TechnicalIndicators


class TechnicalAnalysisEngine:
    """Institutional-grade Technical Analysis and Momentum Indicator Engine."""

    def __init__(
        self,
        ema_fast: int = 20,
        ema_medium: int = 50,
        ema_slow: int = 200,
        rsi_period: int = 14,
        bollinger_window: int = 20,
        bollinger_std: float = 2.0,
        atr_period: int = 14,
    ):
        self.ema_fast = ema_fast
        self.ema_medium = ema_medium
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period
        self.bollinger_window = bollinger_window
        self.bollinger_std = bollinger_std
        self.atr_period = atr_period

    def compute_indicators(self, df: pd.DataFrame) -> TechnicalIndicators:
        """Calculates full technical indicators from OHLCV series."""
        if len(df) < 30:
            raise ValueError(f"Insufficient data for technical analysis. Need >= 30 bars, got {len(df)}")

        close = df["Close"].copy()
        high = df["High"].copy()
        low = df["Low"].copy()

        # EMAs
        ema_20 = close.ewm(span=self.ema_fast, adjust=False).mean()
        ema_50 = close.ewm(span=self.ema_medium, adjust=False).mean()
        ema_200 = close.ewm(span=min(self.ema_slow, len(df)), adjust=False).mean()

        # RSI (Wilder's Smoothing)
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1.0 / self.rsi_period, min_periods=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / self.rsi_period, min_periods=self.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi = rsi.fillna(50.0)

        # MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - macd_signal

        # Bollinger Bands
        sma_20 = close.rolling(window=self.bollinger_window).mean()
        std_20 = close.rolling(window=self.bollinger_window).std()
        bb_upper = sma_20 + (self.bollinger_std * std_20)
        bb_lower = sma_20 - (self.bollinger_std * std_20)

        # Average True Range (ATR)
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean().bfill()

        # Latest values
        cur_price = float(close.iloc[-1])
        c_ema20 = float(ema_20.iloc[-1])
        c_ema50 = float(ema_50.iloc[-1])
        c_ema200 = float(ema_200.iloc[-1])
        c_rsi = float(rsi.iloc[-1])
        c_macd = float(macd.iloc[-1])
        c_macd_sig = float(macd_signal.iloc[-1])
        c_macd_hist = float(macd_hist.iloc[-1])
        c_bb_upper = float(bb_upper.iloc[-1]) if not np.isnan(bb_upper.iloc[-1]) else cur_price * 1.05
        c_bb_mid = float(sma_20.iloc[-1]) if not np.isnan(sma_20.iloc[-1]) else cur_price
        c_bb_lower = float(bb_lower.iloc[-1]) if not np.isnan(bb_lower.iloc[-1]) else cur_price * 0.95
        c_atr = float(atr.iloc[-1])

        # Trend & RSI condition signals
        if cur_price > c_ema20 > c_ema50 > c_ema200:
            trend_signal = "STRONG_BULLISH"
        elif cur_price > c_ema50:
            trend_signal = "MODERATELY_BULLISH"
        elif cur_price < c_ema20 < c_ema50 < c_ema200:
            trend_signal = "STRONG_BEARISH"
        elif cur_price < c_ema50:
            trend_signal = "MODERATELY_BEARISH"
        else:
            trend_signal = "CONSOLIDATION_NEUTRAL"

        if c_rsi >= 70.0:
            rsi_condition = "OVERBOUGHT"
        elif c_rsi <= 30.0:
            rsi_condition = "OVERSOLD"
        else:
            rsi_condition = "NEUTRAL"

        return TechnicalIndicators(
            current_price=round(cur_price, 2),
            ema_20=round(c_ema20, 2),
            ema_50=round(c_ema50, 2),
            ema_200=round(c_ema200, 2),
            rsi_14=round(c_rsi, 2),
            macd=round(c_macd, 3),
            macd_signal=round(c_macd_sig, 3),
            macd_hist=round(c_macd_hist, 3),
            bollinger_upper=round(c_bb_upper, 2),
            bollinger_middle=round(c_bb_mid, 2),
            bollinger_lower=round(c_bb_lower, 2),
            atr_14=round(c_atr, 2),
            trend_signal=trend_signal,
            rsi_condition=rsi_condition,
        )
