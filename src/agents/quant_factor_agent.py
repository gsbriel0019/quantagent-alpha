import numpy as np
import pandas as pd
from typing import Tuple
from src.agents.base import BaseAgent
from src.models.schemas import QuantFactors, TechnicalIndicators, FibonacciLevels
from src.indicators.technical import TechnicalAnalysisEngine
from src.indicators.fibonacci import FibonacciRetracementEngine


class QuantFactorAgent(BaseAgent):
    """Institutional Quantitative and Statistical Factor Agent."""

    def __init__(self, risk_free_rate: float = 0.045):
        super().__init__(
            name="QuantFactorAgent",
            role="Quantitative Risk Modeling, Technical Factors & Fibonacci Geometry"
        )
        self.risk_free_rate = risk_free_rate
        self.tech_engine = TechnicalAnalysisEngine()
        self.fibo_engine = FibonacciRetracementEngine()

    def run(
        self,
        ticker: str,
        asset_df: pd.DataFrame,
        benchmark_df: pd.DataFrame
    ) -> Tuple[QuantFactors, TechnicalIndicators, FibonacciLevels]:
        """Performs rigorous factor modeling and statistical calculations."""
        clean_ticker = ticker.strip().upper()

        # Compute price returns
        asset_prices = asset_df["Close"].dropna()
        bench_prices = benchmark_df["Close"].dropna()

        # Align series dates
        aligned = pd.concat([asset_prices, bench_prices], axis=1, join="inner").dropna()
        asset_aligned = aligned.iloc[:, 0]
        bench_aligned = aligned.iloc[:, 1]

        asset_returns = np.log(asset_aligned / asset_aligned.shift(1)).dropna()
        bench_returns = np.log(bench_aligned / bench_aligned.shift(1)).dropna()

        if len(asset_returns) < 20:
            raise ValueError(f"Insufficient return series for {clean_ticker}: got {len(asset_returns)} observations")

        # Annualized Statistics (252 trading days)
        mean_daily = float(asset_returns.mean())
        std_daily = float(asset_returns.std())
        ann_return = mean_daily * 252
        ann_vol = std_daily * np.sqrt(252) if std_daily > 0 else 0.0001

        # Sharpe Ratio
        sharpe = (ann_return - self.risk_free_rate) / ann_vol

        # Downside Volatility & Sortino Ratio
        downside_returns = asset_returns[asset_returns < 0]
        downside_std = float(downside_returns.std()) if len(downside_returns) > 0 else std_daily
        downside_ann_vol = downside_std * np.sqrt(252) if downside_std > 0 else 0.0001
        sortino = (ann_return - self.risk_free_rate) / downside_ann_vol

        # Maximum Drawdown (Peak to Trough)
        cum_returns = np.exp(np.cumsum(asset_returns))
        running_max = np.maximum.accumulate(cum_returns)
        drawdowns = (cum_returns - running_max) / running_max
        max_dd = float(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0
        calmar = (ann_return / abs(max_dd)) if abs(max_dd) > 0.001 else 0.0

        # Beta & Jensen's Alpha against Benchmark
        cov_matrix = np.cov(asset_returns, bench_returns)
        var_bench = cov_matrix[1, 1]
        cov_asset_bench = cov_matrix[0, 1]
        beta = float(cov_asset_bench / var_bench) if var_bench > 0 else 1.0

        bench_ann_return = float(bench_returns.mean()) * 252
        alpha = (ann_return - self.risk_free_rate) - beta * (bench_ann_return - self.risk_free_rate)

        # Value-at-Risk (95% Daily) & Conditional VaR (Expected Shortfall)
        var_95_hist = -float(np.percentile(asset_returns, 5))
        tail_losses = asset_returns[asset_returns <= -var_95_hist]
        cvar_95 = -float(tail_losses.mean()) if len(tail_losses) > 0 else var_95_hist * 1.25

        # Win Rate & Profit Factor
        positive_days = asset_returns[asset_returns > 0]
        negative_days = asset_returns[asset_returns < 0]
        win_rate = float(len(positive_days) / len(asset_returns)) if len(asset_returns) > 0 else 0.5
        gross_profits = positive_days.sum()
        gross_losses = abs(negative_days.sum()) if len(negative_days) > 0 else 0.0001
        profit_factor = float(gross_profits / gross_losses) if gross_losses > 0 else 1.0

        # Compute Technical Indicators & Fibonacci Retracements
        tech_indicators = self.tech_engine.compute_indicators(asset_df)
        fibo_levels = self.fibo_engine.compute_levels(asset_df)

        factors = QuantFactors(
            ticker=clean_ticker,
            annualized_return=round(ann_return, 4),
            annualized_volatility=round(ann_vol, 4),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            calmar_ratio=round(calmar, 2),
            max_drawdown=round(max_dd, 4),
            beta_to_sp500=round(beta, 2),
            alpha_annualized=round(alpha, 4),
            daily_var_95=round(var_95_hist, 4),
            daily_cvar_95=round(cvar_95, 4),
            win_rate=round(win_rate, 4),
            profit_factor=round(profit_factor, 2),
        )

        return factors, tech_indicators, fibo_levels
