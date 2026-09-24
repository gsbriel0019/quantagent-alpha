import argparse
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from tabulate import tabulate
from src.agents.thesis_synthesizer import ThesisSynthesizerAgent
from src.reporting.investment_memo import InvestmentMemoGenerator


def main():
    parser = argparse.ArgumentParser(
        description="QuantAgent-Alpha: Institutional Autonomous Investment Thesis Runner"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default="NVDA",
        help="Asset ticker symbol (e.g., NVDA, AAPL, MSFT, TSLA, SPY)"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="^GSPC",
        help="Market benchmark index ticker (default: ^GSPC)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="1y",
        help="Historical lookback period (e.g., 6mo, 1y, 2y)"
    )
    parser.add_argument(
        "--save-memo",
        action="store_true",
        help="Save generated Markdown memorandum to file"
    )

    args = parser.parse_args()
    ticker = args.ticker.upper().strip()

    print(f"\n" + "=" * 70)
    print(f"🏛️  QUANTAGENT-ALPHA: MULTI-AGENT QUANTITATIVE ENGINE")
    print(f"Author: Gabriel Proaño (@gsbriel0019)")
    print(f"Target Ticker: {ticker} | Benchmark: {args.benchmark} | Horizon: {args.period}")
    print("=" * 70)

    synthesizer = ThesisSynthesizerAgent()

    try:
        print("\n[*] Initializing Agents & Ingesting Market Geometry...")
        thesis = synthesizer.timed_run(
            ticker=ticker,
            benchmark=args.benchmark,
            period=args.period
        )

        q = thesis.quantitative_factors
        t = thesis.technical_analysis
        f = thesis.fibonacci_framework
        r = thesis.risk_management
        s = thesis.sentiment_analysis
        m = thesis.macro_environment

        print("\n" + "-" * 70)
        print(f"📌 EXECUTIVE VERDICT: {thesis.conviction_rating.value} (Confidence: {thesis.confidence_score}%)")
        print(f"Current Price: ${thesis.current_price:.2f} | Target (TP1): ${thesis.price_target:.2f} (+{thesis.expected_return_pct:.2f}%)")
        print(f"Risk Audit Verdict: {r.verdict.value} | Max Allocation: {r.max_recommended_allocation * 100:.2f}%")
        print("-" * 70)

        quant_table = [
            ["Annualized Return", f"{q.annualized_return*100:+.2f}%", "> 4.5% Risk Free"],
            ["Annualized Volatility", f"{q.annualized_volatility*100:.2f}%", "< 35.0%"],
            ["Sharpe Ratio", f"{q.sharpe_ratio:.2f}", ">= 0.75"],
            ["Sortino Ratio (Downside)", f"{q.sortino_ratio:.2f}", ">= 1.00"],
            ["Calmar Ratio", f"{q.calmar_ratio:.2f}", ">= 0.50"],
            ["Maximum Drawdown", f"{abs(q.max_drawdown)*100:.2f}%", "<= 28.0%"],
            ["Beta to S&P 500", f"{q.beta_to_sp500:.2f}", "1.00 (Market)"],
            ["Jensen's Alpha", f"{q.alpha_annualized*100:+.2f}%", "> 0.0%"],
            ["Daily 95% VaR / CVaR", f"{q.daily_var_95*100:.2f}% / {q.daily_cvar_95*100:.2f}%", "Fiduciary Limit"],
            ["Win Rate / Profit Factor", f"{q.win_rate*100:.1f}% / {q.profit_factor:.2f}x", "> 1.20x Profit Factor"]
        ]
        print("\n📊 1. Quantitative Factor & Risk Matrix:")
        print(tabulate(quant_table, headers=["Metric", "Value", "Benchmark Target"], tablefmt="grid"))

        fibo_table = [
            ["Swing High (Peak)", f"${f.swing_high:.2f}"],
            ["Fibonacci 23.6%", f"${f.level_236:.2f}"],
            ["Fibonacci 38.2%", f"${f.level_382:.2f}"],
            ["Fibonacci 50.0% (Equilibrium)", f"${f.level_500:.2f}"],
            ["Fibonacci 61.8% (Golden Pocket) 🎯", f"${f.level_618:.2f}"],
            ["Fibonacci 78.6%", f"${f.level_786:.2f}"],
            ["Swing Low (Base)", f"${f.swing_low:.2f}"],
            ["Immediate Support / Resistance", f"${f.nearest_support:.2f} / ${f.nearest_resistance:.2f}"],
        ]
        print(f"\n📐 2. Fibonacci Retracement Framework ({f.trend_direction}):")
        print(tabulate(fibo_table, headers=["Structure Level", "Price"], tablefmt="grid"))

        trade_plan_table = [
            ["Reference Entry", f"${thesis.actionable_trade_plan['entry_reference_price']:.2f}"],
            ["Stop Loss Limit", f"${thesis.actionable_trade_plan['stop_loss_price']:.2f} (-{r.suggested_stop_loss_pct:.2f}%)"],
            ["Take Profit 1 (Target)", f"${thesis.actionable_trade_plan['take_profit_target_1']:.2f}"],
            ["Take Profit 2 (Extension)", f"${thesis.actionable_trade_plan['take_profit_target_2']:.2f}"],
            ["Risk-to-Reward Ratio", f"{thesis.actionable_trade_plan['risk_reward_ratio']:.2f} : 1.0"],
            ["Disciplined Portfolio Allocation", f"{thesis.actionable_trade_plan['recommended_allocation_pct']:.2f}% of capital"],
        ]
        print("\n🛡️ 3. Actionable Institutional Execution Plan:")
        print(tabulate(trade_plan_table, headers=["Execution Parameter", "Specification"], tablefmt="grid"))

        if args.save_memo:
            memo_text = InvestmentMemoGenerator.generate_markdown_memo(thesis)
            memo_file = Path(f"QuantAgent_Alpha_Memo_{ticker}.md")
            memo_file.write_text(memo_text, encoding="utf-8")
            print(f"\n[✓] Executive Memorandum saved to: {memo_file.resolve()}")

        print("\n" + "=" * 70)
        print("Analysis completed successfully. Powered by QuantAgent-Alpha.")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[!] Execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
