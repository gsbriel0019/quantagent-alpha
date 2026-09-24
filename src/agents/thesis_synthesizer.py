from datetime import datetime
from typing import Optional
import numpy as np
from src.agents.base import BaseAgent
from src.agents.quant_factor_agent import QuantFactorAgent
from src.agents.macro_sentiment_agent import MacroSentimentAgent
from src.agents.risk_auditor_agent import RiskAuditorAgent
from src.data.market_data import MarketDataLoader
from src.models.schemas import (
    InvestmentThesis,
    ConvictionRating,
    RiskAuditVerdict,
)


class ThesisSynthesizerAgent(BaseAgent):
    """Institutional Multi-Agent Orchestrator and Investment Thesis Synthesizer."""

    def __init__(self, risk_free_rate: float = 0.045):
        super().__init__(
            name="ThesisSynthesizerAgent",
            role="Multi-Agent Pipeline Orchestration & Executive Thesis Synthesis"
        )
        self.market_loader = MarketDataLoader()
        self.quant_agent = QuantFactorAgent(risk_free_rate=risk_free_rate)
        self.macro_agent = MacroSentimentAgent()
        self.risk_agent = RiskAuditorAgent()

    def run(
        self,
        ticker: str,
        benchmark: str = "^GSPC",
        period: str = "1y",
        company_name: Optional[str] = None
    ) -> InvestmentThesis:
        """Executes the full multi-agent analytical pipeline and synthesizes the thesis."""
        clean_ticker = ticker.strip().upper()

        # Step 1: Ingest asset & benchmark market data
        asset_df, bench_df = self.market_loader.fetch_pair_data(
            ticker=clean_ticker,
            benchmark=benchmark,
            period=period
        )

        # Step 2: Quant & Technical Factor Agent
        factors, tech, fibo = self.quant_agent.timed_run(
            ticker=clean_ticker,
            asset_df=asset_df,
            benchmark_df=bench_df
        )

        # Step 3: Macro & Sentiment Agent
        macro, sentiment, news = self.macro_agent.timed_run(
            ticker=clean_ticker,
            price_trend_signal=tech.trend_signal
        )

        # Step 4: Risk Auditor Agent
        risk_audit = self.risk_agent.timed_run(
            quant_factors=factors,
            technical=tech,
            fibo=fibo,
            macro=macro
        )

        # Step 5: Multi-Factor Scoring & Conviction Synthesis
        # Quant Score (0 - 100)
        sharpe_pts = min(max(factors.sharpe_ratio * 25.0, 0.0), 40.0)
        win_rate_pts = factors.win_rate * 30.0
        trend_pts = 30.0 if "BULLISH" in tech.trend_signal else (15.0 if "NEUTRAL" in tech.trend_signal else 5.0)
        quant_score = sharpe_pts + win_rate_pts + trend_pts

        # Macro/Sentiment Score (0 - 100)
        vix_pts = 30.0 if macro.vix_level < 18.0 else (15.0 if macro.vix_level < 25.0 else 5.0)
        sentiment_pts = (sentiment.aggregate_score + 1.0) * 25.0  # maps -1..1 to 0..50
        regime_pts = 20.0 if macro.macro_regime.value in ["EXPANSION_RISK_ON", "RECOVERY"] else 10.0
        macro_score = vix_pts + sentiment_pts + regime_pts

        # Risk Score (0 - 100)
        risk_score = 100.0 if risk_audit.verdict == RiskAuditVerdict.APPROVED else (
            60.0 if risk_audit.verdict == RiskAuditVerdict.APPROVED_WITH_CONDITIONS else 20.0
        )

        # Composite Conviction Score
        composite_score = (0.45 * quant_score) + (0.25 * macro_score) + (0.30 * risk_score)
        composite_score = float(np.clip(composite_score, 5.0, 98.0))

        # Conviction Rating
        if risk_audit.verdict == RiskAuditVerdict.REJECTED:
            conviction = ConvictionRating.SELL
        elif composite_score >= 75.0:
            conviction = ConvictionRating.STRONG_BUY
        elif composite_score >= 60.0:
            conviction = ConvictionRating.BUY
        elif composite_score >= 45.0:
            conviction = ConvictionRating.NEUTRAL
        elif composite_score >= 32.0:
            conviction = ConvictionRating.REDUCE
        else:
            conviction = ConvictionRating.SELL

        # Price Target & Expected Return
        current_price = tech.current_price
        target_price = risk_audit.suggested_take_profit_1
        expected_return_pct = round(((target_price - current_price) / current_price) * 100.0, 2)

        # Generate Executive Summary
        summary = (
            f"Institutional Quantitative Memo for {clean_ticker}: Conviction rated as {conviction.value} "
            f"with a composite confidence rating of {composite_score:.1f}%. "
            f"The asset displays {tech.trend_signal.lower().replace('_', ' ')} momentum with an annualized Sharpe ratio of {factors.sharpe_ratio:.2f} "
            f"and beta of {factors.beta_to_sp500:.2f} relative to the S&P 500. "
            f"Fibonacci geometry establishes key institutional support at ${fibo.nearest_support:.2f} and resistance at ${fibo.nearest_resistance:.2f}. "
            f"The macroeconomic backdrop aligns with {macro.macro_regime.value.lower().replace('_', ' ')} while news sentiment registers {sentiment.overall_sentiment.lower().replace('_', ' ')} "
            f"({sentiment.aggregate_score:+.2f}). "
            f"Risk Governance verdict: {risk_audit.verdict.value} with disciplined volatility-targeted allocation capped at {risk_audit.max_recommended_allocation*100:.1f}%."
        )

        trade_plan = {
            "entry_reference_price": current_price,
            "stop_loss_price": risk_audit.suggested_stop_loss_price,
            "take_profit_target_1": risk_audit.suggested_take_profit_1,
            "take_profit_target_2": risk_audit.suggested_take_profit_2,
            "risk_reward_ratio": risk_audit.risk_reward_ratio,
            "recommended_allocation_pct": round(risk_audit.max_recommended_allocation * 100.0, 2),
        }

        catalysts = [
            f"Technical momentum: Price trades above key moving averages with RSI at {tech.rsi_14:.1f}.",
            f"Golden pocket support: Retracement structure anchored at ${fibo.level_618:.2f}.",
            f"Sentiment momentum: {sentiment.bullish_mentions} bullish catalysts identified in recent corporate communications."
        ]

        risks = [
            f"Tail-risk exposure: Daily 95% Expected Shortfall (CVaR) estimated at {factors.daily_cvar_95*100:.2f}%.",
            f"Macro sensitivity: US 10Y Yield at {macro.yield_10y*100:.2f}% and Fed policy rate at {macro.fed_funds_rate*100:.2f}%.",
            f"Historical peak drawdown: Recorded maximum drawdown of {abs(factors.max_drawdown)*100:.1f}%."
        ]

        return InvestmentThesis(
            ticker=clean_ticker,
            company_name=company_name or clean_ticker,
            as_of_date=datetime.now().strftime("%Y-%m-%d"),
            conviction_rating=conviction,
            confidence_score=round(composite_score, 1),
            price_target=round(target_price, 2),
            current_price=round(current_price, 2),
            expected_return_pct=expected_return_pct,
            time_horizon="3 to 6 Months (Institutional Swing / Tactical Allocation)",
            executive_summary=summary,
            technical_analysis=tech,
            fibonacci_framework=fibo,
            quantitative_factors=factors,
            macro_environment=macro,
            sentiment_analysis=sentiment,
            risk_management=risk_audit,
            catalysts=catalysts,
            primary_risks=risks,
            actionable_trade_plan=trade_plan,
        )
