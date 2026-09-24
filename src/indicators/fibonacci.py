import numpy as np
import pandas as pd
from src.models.schemas import FibonacciLevels


class FibonacciRetracementEngine:
    """Calculates Swing High, Swing Low, and Golden Ratio Fibonacci Retracement Levels."""

    def __init__(self, lookback_window: int = 60):
        self.lookback_window = lookback_window

    def compute_levels(self, df: pd.DataFrame) -> FibonacciLevels:
        """Computes key Fibonacci levels from recent high/low swing structure."""
        if len(df) < self.lookback_window:
            window_df = df
        else:
            window_df = df.iloc[-self.lookback_window:]

        swing_high = float(window_df["High"].max())
        swing_low = float(window_df["Low"].min())
        current_price = float(window_df["Close"].iloc[-1])

        high_idx = window_df["High"].idxmax()
        low_idx = window_df["Low"].idxmin()

        diff = swing_high - swing_low
        if diff == 0:
            diff = swing_high * 0.01

        # Determine dominant swing direction
        if high_idx > low_idx:
            # Uptrend: retracement from high towards low
            trend_direction = "UPTREND"
            level_0 = swing_high
            level_236 = swing_high - (0.236 * diff)
            level_382 = swing_high - (0.382 * diff)
            level_500 = swing_high - (0.500 * diff)
            level_618 = swing_high - (0.618 * diff)  # Golden pocket
            level_786 = swing_high - (0.786 * diff)
            level_100 = swing_low
        else:
            # Downtrend: retracement from low towards high
            trend_direction = "DOWNTREND"
            level_0 = swing_low
            level_236 = swing_low + (0.236 * diff)
            level_382 = swing_low + (0.382 * diff)
            level_500 = swing_low + (0.500 * diff)
            level_618 = swing_low + (0.618 * diff)
            level_786 = swing_low + (0.786 * diff)
            level_100 = swing_high

        all_levels = [level_0, level_236, level_382, level_500, level_618, level_786, level_100]
        below_price = [lvl for lvl in all_levels if lvl < current_price]
        above_price = [lvl for lvl in all_levels if lvl > current_price]

        nearest_support = max(below_price) if below_price else swing_low
        nearest_resistance = min(above_price) if above_price else swing_high

        return FibonacciLevels(
            swing_high=round(swing_high, 2),
            swing_low=round(swing_low, 2),
            trend_direction=trend_direction,
            level_0=round(level_0, 2),
            level_236=round(level_236, 2),
            level_382=round(level_382, 2),
            level_500=round(level_500, 2),
            level_618=round(level_618, 2),
            level_786=round(level_786, 2),
            level_100=round(level_100, 2),
            nearest_support=round(nearest_support, 2),
            nearest_resistance=round(nearest_resistance, 2),
        )
