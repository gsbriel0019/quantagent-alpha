from src.models.schemas import InvestmentThesis


class InvestmentMemoGenerator:
    """Institutional Markdown and HTML Investment Memorandum Generator."""

    @staticmethod
    def generate_markdown_memo(thesis: InvestmentThesis) -> str:
        """Generates a professional Markdown Investment Memorandum."""
        q = thesis.quantitative_factors
        t = thesis.technical_analysis
        f = thesis.fibonacci_framework
        m = thesis.macro_environment
        s = thesis.sentiment_analysis
        r = thesis.risk_management

        conviction_badge = {
            "STRONG_BUY": "🟢 **STRONG BUY**",
            "BUY": "🟢 **BUY**",
            "NEUTRAL": "🟡 **NEUTRAL / HOLD**",
            "REDUCE": "🟠 **REDUCE**",
            "SELL": "🔴 **SELL**",
        }.get(thesis.conviction_rating.value, thesis.conviction_rating.value)

        verdict_badge = {
            "APPROVED": "✅ **APPROVED**",
            "APPROVED_WITH_CONDITIONS": "⚠️ **APPROVED WITH CONDITIONS**",
            "REJECTED": "❌ **REJECTED**",
        }.get(r.verdict.value, r.verdict.value)

        memo = f"""# 🏛️ Institutional Investment Memorandum: {thesis.ticker}

**Date:** {thesis.as_of_date} | **Analyst Group:** QuantAgent-Alpha Autonomous Multi-Agent System  
**Lead Author:** Gabriel Proaño (@gsbriel0019) | **Horizon:** {thesis.time_horizon}

---

## 📌 Executive Summary

- **Recommendation:** {conviction_badge}
- **Confidence Rating:** `{thesis.confidence_score}%`
- **Current Reference Price:** `${thesis.current_price:.2f}`
- **Institutional Price Target:** `${thesis.price_target:.2f}` (+{thesis.expected_return_pct:.2f}%)
- **Risk Governance Verdict:** {verdict_badge}
- **Recommended Max Portfolio Weight:** `{r.max_recommended_allocation * 100:.2f}%`

> {thesis.executive_summary}

---

## 📊 1. Quantitative Factor & Risk Engine

| Metric | Asset Value | Benchmark (S&P 500) | Policy Threshold | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Annualized Return** | `{q.annualized_return * 100:+.2f}%` | `+12.00%` | > Risk-Free Rate (4.5%) | {"✅" if q.annualized_return > 0.045 else "⚠️"} |
| **Annualized Volatility** | `{q.annualized_volatility * 100:.2f}%` | `16.50%` | <= 35.00% | {"✅" if q.annualized_volatility <= 0.35 else "⚠️"} |
| **Sharpe Ratio** | `{q.sharpe_ratio:.2f}` | `0.65` | >= 0.75 | {"✅" if r.sharpe_check else "❌"} |
| **Sortino Ratio (Downside)** | `{q.sortino_ratio:.2f}` | `0.85` | >= 1.00 | {"✅" if q.sortino_ratio >= 1.0 else "⚠️"} |
| **Calmar Ratio** | `{q.calmar_ratio:.2f}` | `0.70` | >= 0.50 | {"✅" if q.calmar_ratio >= 0.5 else "⚠️"} |
| **Maximum Drawdown** | `{abs(q.max_drawdown) * 100:.2f}%` | `19.20%` | <= 28.00% | {"✅" if r.drawdown_check else "❌"} |
| **Beta to Market** | `{q.beta_to_sp500:.2f}` | `1.00` | Cyclical Factor | ℹ️ |
| **Jensen's Alpha (Ann.)** | `{q.alpha_annualized * 100:+.2f}%` | `0.00%` | > 0.00% | {"✅" if q.alpha_annualized > 0 else "⚠️"} |
| **Daily 95% VaR** | `{q.daily_var_95 * 100:.2f}%` | `1.65%` | <= 4.50% | {"✅" if r.var_check else "❌"} |
| **Daily 95% CVaR (Tail Risk)** | `{q.daily_cvar_95 * 100:.2f}%` | `2.45%` | Fiduciary Metric | ℹ️ |
| **Win Rate / Profit Factor** | `{q.win_rate * 100:.1f}%` / `{q.profit_factor:.2f}x` | `53.0% / 1.15x` | Profit Factor > 1.2x | {"✅" if q.profit_factor >= 1.2 else "⚠️"} |

---

## 📐 2. Technical Framework & Fibonacci Geometry

- **Trend Signal:** `{t.trend_signal}`
- **Moving Average Alignment:** EMA20 (${t.ema_20:.2f}) vs EMA50 (${t.ema_50:.2f}) vs EMA200 (${t.ema_200:.2f})
- **RSI (14-period Wilder):** `{t.rsi_14:.2f}` (`{t.rsi_condition}`)
- **MACD (12, 26, 9):** `{t.macd:.2f}` (Signal: `{t.macd_signal:.2f}`, Hist: `{t.macd_hist:+.2f}`)
- **Bollinger Bands:** Upper `${t.bollinger_upper:.2f}` | Middle `${t.bollinger_middle:.2f}` | Lower `${t.bollinger_lower:.2f}`
- **Average True Range (ATR 14):** `${t.atr_14:.2f}`

### Fibonacci Retracement Levels ({f.trend_direction})
* **Swing High:** `${f.swing_high:.2f}`
* **Fib 23.6%:** `${f.level_236:.2f}`
* **Fib 38.2%:** `${f.level_382:.2f}`
* **Fib 50.0% (Equilibrium):** `${f.level_500:.2f}`
* **Fib 61.8% (Golden Pocket):** `${f.level_618:.2f}` 🎯
* **Fib 78.6%:** `${f.level_786:.2f}`
* **Swing Low (Base):** `${f.swing_low:.2f}`
* **Immediate Support / Resistance:** Support `${f.nearest_support:.2f}` | Resistance `${f.nearest_resistance:.2f}`

---

## 🌍 3. Macroeconomic Environment & NLP Sentiment

### Macro Cycle Indicators
* **Regime State:** `{m.macro_regime.value}`
* **Policy Rate (Fed Funds):** `{m.fed_funds_rate * 100:.2f}%`
* **US CPI Inflation:** `{m.us_cpi_inflation * 100:.2f}%`
* **US 10Y Treasury Yield:** `{m.yield_10y * 100:.2f}%` | **US 2Y Yield:** `{m.yield_2y * 100:.2f}%`
* **Yield Curve Spread (10Y - 2Y):** `{m.yield_curve_spread * 100:+.2f} bps` (Inverted: `{m.is_yield_curve_inverted}`)
* **VIX Volatility Level:** `{m.vix_level:.2f}` (`{m.vix_regime}`)

### NLP Financial Sentiment
* **Aggregate Sentiment Polarity:** `{s.aggregate_score:+.2f}` (`{s.overall_sentiment}`)
* **Catalyst Breakdown:** `{s.bullish_mentions}` Bullish / `{s.bearish_mentions}` Bearish / `{s.neutral_mentions}` Neutral
* **Price / Sentiment Divergence:** `{s.sentiment_price_divergence}`

---

## 🛡️ 4. Institutional Risk Governance & Actionable Trade Plan

### Mandate Compliance Audit
{chr(10).join(f"- {note}" for note in r.audit_notes)}

### Position Sizing & Execution Mandates
* **Volatility Target Allocation (18% target vol):** `{r.volatility_target_size * 100:.2f}%`
* **Fractional Kelly Criterion (50% Kelly):** `{r.fractional_kelly_size * 100:.2f}%`
* **Risk-Adjusted Cap Allocation:** `{r.max_recommended_allocation * 100:.2f}% of portfolio`
* **Stop Loss Order:** `${r.suggested_stop_loss_price:.2f}` (-{r.suggested_stop_loss_pct:.2f}%)
* **Take Profit Target 1 (TP1):** `${r.suggested_take_profit_1:.2f}`
* **Take Profit Target 2 (TP2 / Extension):** `${r.suggested_take_profit_2:.2f}`
* **Risk-to-Reward Ratio:** `{r.risk_reward_ratio:.2f} : 1.0`

---
*Report auto-generated by QuantAgent-Alpha Suite. Designed & Engineered by Gabriel Proaño.*
"""
        return memo
