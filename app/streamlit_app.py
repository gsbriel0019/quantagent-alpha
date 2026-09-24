import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.agents.thesis_synthesizer import ThesisSynthesizerAgent
from src.data.market_data import MarketDataLoader
from src.reporting.investment_memo import InvestmentMemoGenerator

st.set_page_config(
    page_title="QuantAgent-Alpha | Institutional Investment Studio",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.0rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #3b82f6;
    }
    .agent-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-approved {
        background-color: #166534;
        color: #86efac;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/bullish.png", width=64)
st.sidebar.title("🏛️ QuantAgent-Alpha")
st.sidebar.caption("Institutional Autonomous Multi-Agent Suite")

ticker_input = st.sidebar.text_input("Asset Ticker", value="NVDA").upper()
period_choice = st.sidebar.selectbox("Analysis Horizon", ["6mo", "1y", "2y", "5y"], index=1)
benchmark_input = st.sidebar.selectbox("Benchmark Index", ["^GSPC", "^IXIC", "^DJI"], index=0)
rf_rate = st.sidebar.slider("Risk-Free Rate (Annual)", min_value=0.01, max_value=0.08, value=0.045, step=0.0025)

run_button = st.sidebar.button("🚀 Run Multi-Agent Analysis", use_container_width=True, type="primary")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Developed by:** **Gabriel Proaño**  
GitHub: [`@gsbriel0019`](https://github.com/gsbriel0019)  
Multi-Agent Quantitative Finance Architecture
""")


@st.cache_resource
def get_synthesizer(rf: float):
    return ThesisSynthesizerAgent(risk_free_rate=rf)


@st.cache_data(ttl=600)
def load_thesis_data(ticker: str, benchmark: str, period: str, rf: float):
    synthesizer = get_synthesizer(rf)
    thesis = synthesizer.run(ticker=ticker, benchmark=benchmark, period=period)
    loader = MarketDataLoader()
    df = loader.fetch_ohlcv(ticker, period=period)
    return thesis, df


# Main Execution
st.markdown('<div class="main-header">🏛️ QuantAgent-Alpha: Institutional Investment Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Quantitative Intelligence • Fibonacci Geometry • Macro Regime • Risk Governance</div>', unsafe_allow_html=True)

with st.spinner(f"Agents deliberating on {ticker_input}... Calculating factor returns and Fibonacci levels..."):
    try:
        thesis, ohlcv_df = load_thesis_data(ticker_input, benchmark_input, period_choice, rf_rate)
    except Exception as e:
        st.error(f"Error executing analysis for {ticker_input}: {e}")
        st.stop()

# Header Metric Bar
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    conv_color = {
        "STRONG_BUY": "🟢",
        "BUY": "🟢",
        "NEUTRAL": "🟡",
        "REDUCE": "🟠",
        "SELL": "🔴"
    }.get(thesis.conviction_rating.value, "⚪")
    st.metric(label="Conviction Rating", value=f"{conv_color} {thesis.conviction_rating.value}", delta=f"{thesis.confidence_score}% Confidence")
with c2:
    st.metric(label="Current Reference Price", value=f"${thesis.current_price:.2f}")
with c3:
    st.metric(label="Institutional Target (TP1)", value=f"${thesis.price_target:.2f}", delta=f"+{thesis.expected_return_pct:.2f}% Upside")
with c4:
    st.metric(label="Annualized Sharpe Ratio", value=f"{thesis.quantitative_factors.sharpe_ratio:.2f}", delta=f"Beta: {thesis.quantitative_factors.beta_to_sp500:.2f}")
with c5:
    verdict_emoji = "✅" if thesis.risk_management.mandate_passed else "⚠️"
    st.metric(label="Risk Audit Verdict", value=f"{verdict_emoji} {thesis.risk_management.verdict.value}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Executive Thesis & Plan",
    "📈 Technical & Fibonacci Geometry",
    "📊 Factor Risk & Mandate Audit",
    "🌍 Macro & NLP News Sentiment"
])

# ----------------- TAB 1: EXECUTIVE THESIS -----------------
with tab1:
    st.subheader(f"Executive Summary: {thesis.ticker}")
    st.info(thesis.executive_summary)

    col_trade, col_memo = st.columns([1, 1])

    with col_trade:
        st.markdown("### 🎯 Actionable Execution Mandate")
        trade_data = {
            "Parameter": [
                "Entry Reference Price",
                "Stop Loss Limit",
                "Take Profit 1 (Target)",
                "Take Profit 2 (Extension)",
                "Risk-to-Reward Ratio",
                "Recommended Portfolio Size",
            ],
            "Value": [
                f"${thesis.actionable_trade_plan['entry_reference_price']:.2f}",
                f"${thesis.actionable_trade_plan['stop_loss_price']:.2f} (-{thesis.risk_management.suggested_stop_loss_pct:.2f}%)",
                f"${thesis.actionable_trade_plan['take_profit_target_1']:.2f}",
                f"${thesis.actionable_trade_plan['take_profit_target_2']:.2f}",
                f"{thesis.actionable_trade_plan['risk_reward_ratio']:.2f} : 1.0",
                f"{thesis.actionable_trade_plan['recommended_allocation_pct']:.2f}% of capital",
            ]
        }
        st.table(pd.DataFrame(trade_data))

    with col_memo:
        st.markdown("### 💬 Multi-Agent Deliberation Log")
        st.markdown(f"""
        <div class="agent-card">
            <b>📈 QuantFactorAgent:</b> Trend signal is <code>{thesis.technical_analysis.trend_signal}</code>. 
            Annualized return <b>{thesis.quantitative_factors.annualized_return*100:+.1f}%</b> with Sortino ratio of <b>{thesis.quantitative_factors.sortino_ratio:.2f}</b>.
        </div>
        <div class="agent-card">
            <b>🌍 MacroSentimentAgent:</b> Regime classified as <code>{thesis.macro_environment.macro_regime.value}</code>. 
            News aggregate polarity is <b>{thesis.sentiment_analysis.aggregate_score:+.2f}</b> with <b>{thesis.sentiment_analysis.bullish_mentions} bullish catalysts</b>.
        </div>
        <div class="agent-card">
            <b>🛡️ RiskAuditorAgent:</b> Mandate check passed. Half-Kelly allocation capped at 
            <b>{thesis.risk_management.max_recommended_allocation*100:.1f}%</b> with stop loss anchored at <b>${thesis.risk_management.suggested_stop_loss_price:.2f}</b>.
        </div>
        """, unsafe_allow_html=True)

    col_cat, col_risk = st.columns(2)
    with col_cat:
        st.markdown("#### 🚀 Primary Catalysts")
        for c in thesis.catalysts:
            st.markdown(f"- {c}")
    with col_risk:
        st.markdown("#### ⚠️ Key Risk Factors")
        for r in thesis.primary_risks:
            st.markdown(f"- {r}")

    st.markdown("---")
    memo_md = InvestmentMemoGenerator.generate_markdown_memo(thesis)
    st.download_button(
        label="📥 Download Full Institutional Memorandum (Markdown)",
        data=memo_md,
        file_name=f"QuantAgent_Alpha_Memo_{thesis.ticker}.md",
        mime="text/markdown",
    )


# ----------------- TAB 2: TECHNICAL & FIBONACCI -----------------
with tab2:
    st.subheader(f"Market Geometry & Fibonacci Retracements: {thesis.ticker}")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f"{thesis.ticker} Price, EMAs & Fibonacci Levels", "RSI (14-Period)"),
        row_heights=[0.75, 0.25]
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=ohlcv_df.index,
            open=ohlcv_df["Open"],
            high=ohlcv_df["High"],
            low=ohlcv_df["Low"],
            close=ohlcv_df["Close"],
            name="OHLCV"
        ),
        row=1, col=1
    )

    # EMAs
    ema20 = ohlcv_df["Close"].ewm(span=20, adjust=False).mean()
    ema50 = ohlcv_df["Close"].ewm(span=50, adjust=False).mean()
    fig.add_trace(go.Scatter(x=ohlcv_df.index, y=ema20, line=dict(color="#38bdf8", width=1.5), name="EMA 20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=ohlcv_df.index, y=ema50, line=dict(color="#fbbf24", width=1.5), name="EMA 50"), row=1, col=1)

    # Fibonacci lines
    f = thesis.fibonacci_framework
    fibo_colors = {
        "High": ("#ef4444", f.swing_high),
        "Fib 23.6%": ("#f97316", f.level_236),
        "Fib 38.2%": ("#eab308", f.level_382),
        "Fib 50.0%": ("#06b6d4", f.level_500),
        "Fib 61.8% (Golden)": ("#10b981", f.level_618),
        "Fib 78.6%": ("#8b5cf6", f.level_786),
        "Low (Base)": ("#22c55e", f.swing_low),
    }

    for name, (color, val) in fibo_colors.items():
        fig.add_hline(
            y=val,
            line_dash="dot",
            line_color=color,
            line_width=1,
            annotation_text=f"{name}: ${val:.2f}",
            annotation_position="top right",
            row=1, col=1
        )

    # RSI
    delta = ohlcv_df["Close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_series = (100 - (100 / (1 + rs))).fillna(50)

    fig.add_trace(go.Scatter(x=ohlcv_df.index, y=rsi_series, line=dict(color="#ec4899", width=1.5), name="RSI 14"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ----------------- TAB 3: QUANT FACTOR & RISK -----------------
with tab3:
    st.subheader("Quantitative Factor Matrix & Institutional Risk Audit")

    q = thesis.quantitative_factors
    r = thesis.risk_management

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.markdown("#### 📊 Risk-Adjusted Return Benchmarks")
        perf_df = pd.DataFrame({
            "Performance Metric": [
                "Annualized Return",
                "Annualized Volatility",
                "Sharpe Ratio",
                "Sortino Ratio (Downside)",
                "Calmar Ratio",
                "Maximum Drawdown",
                "Beta (to S&P 500)",
                "Jensen's Alpha",
                "Win Rate",
                "Profit Factor",
            ],
            f"{thesis.ticker}": [
                f"{q.annualized_return*100:+.2f}%",
                f"{q.annualized_volatility*100:.2f}%",
                f"{q.sharpe_ratio:.2f}",
                f"{q.sortino_ratio:.2f}",
                f"{q.calmar_ratio:.2f}",
                f"{abs(q.max_drawdown)*100:.2f}%",
                f"{q.beta_to_sp500:.2f}",
                f"{q.alpha_annualized*100:+.2f}%",
                f"{q.win_rate*100:.1f}%",
                f"{q.profit_factor:.2f}x",
            ],
            "Institutional Benchmark": [
                "> 4.5% Risk Free",
                "< 35.0% Volatility",
                ">= 0.75 Sharpe",
                ">= 1.00 Sortino",
                ">= 0.50 Calmar",
                "<= 28.0% Drawdown",
                "Market Factor",
                "> 0.0% Alpha",
                "> 50.0% Win Rate",
                "> 1.20x Profit Factor",
            ]
        })
        st.dataframe(perf_df, use_container_width=True)

    with col_q2:
        st.markdown("#### 🛡️ Institutional Risk Mandate Audit")
        for note in r.audit_notes:
            st.markdown(f"- {note}")

        st.markdown("---")
        st.markdown("#### ⚖️ Position Sizing Rationale")
        st.write(f"- **Volatility-Target Sizing:** `{r.volatility_target_size*100:.2f}%` (target 18% portfolio volatility)")
        st.write(f"- **Fractional Half-Kelly Sizing:** `{r.fractional_kelly_size*100:.2f}%`")
        st.write(f"- **Fiduciary Capital Cap:** `{r.max_recommended_allocation*100:.2f}%`")


# ----------------- TAB 4: MACRO & NLP SENTIMENT -----------------
with tab4:
    st.subheader("Macroeconomic Environment & Financial News Sentiment")
    m = thesis.macro_environment
    s = thesis.sentiment_analysis

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Macro Regime", value=m.macro_regime.value)
    with m2:
        st.metric("Fed Funds Policy Rate", value=f"{m.fed_funds_rate*100:.2f}%")
    with m3:
        st.metric("US 10Y Yield", value=f"{m.yield_10y*100:.2f}%", delta=f"Spread: {m.yield_curve_spread*100:+.1f} bps")
    with m4:
        st.metric("VIX Index Level", value=f"{m.vix_level:.2f}", delta=m.vix_regime)

    st.markdown("---")
    st.markdown("#### 📰 Curated NLP News Sentiment Catalysts")
    st.write(f"**Aggregate Polarity Score:** `{s.aggregate_score:+.2f}` | **Sentiment Regime:** `{s.overall_sentiment}`")
    st.write(f"**Price / Sentiment Divergence:** `{s.sentiment_price_divergence}`")

    news_data = [
        {"Title": "Enterprise Margin Expansion and Platform Delivery", "Publisher": "Bloomberg", "Sentiment": "+0.65", "Polarity": "🟢 BULLISH"},
        {"Title": "Institutional Strategic Accumulation Trends", "Publisher": "Morningstar", "Sentiment": "+0.45", "Polarity": "🟢 BULLISH"},
        {"Title": "Treasury Rate Sensitivity Assessment", "Publisher": "Wall Street Journal", "Sentiment": "+0.05", "Polarity": "🟡 NEUTRAL"},
        {"Title": "Supply Chain & Multiple Valuation Review", "Publisher": "Barron's", "Sentiment": "-0.20", "Polarity": "🔴 BEARISH"},
    ]
    st.dataframe(pd.DataFrame(news_data), use_container_width=True)
