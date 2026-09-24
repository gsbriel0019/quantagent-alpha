import numpy as np
from src.agents.base import BaseAgent
from src.models.schemas import (
    RiskAudit,
    RiskAuditVerdict,
    QuantFactors,
    TechnicalIndicators,
    FibonacciLevels,
    MacroRegime,
)


class RiskAuditorAgent(BaseAgent):
    """Institutional Risk Management, Mandate Compliance & Position Sizing Auditor."""

    def __init__(
        self,
        min_sharpe: float = 0.75,
        max_drawdown_limit: float = 0.28,
        var_limit: float = 0.045,
        target_annual_vol: float = 0.18,
        max_allocation_cap: float = 0.20,
    ):
        super().__init__(
            name="RiskAuditorAgent",
            role="Portfolio Risk Governance, Mandate Auditing & Position Sizing"
        )
        self.min_sharpe = min_sharpe
        self.max_drawdown_limit = max_drawdown_limit
        self.var_limit = var_limit
        self.target_annual_vol = target_annual_vol
        self.max_allocation_cap = max_allocation_cap

    def run(
        self,
        quant_factors: QuantFactors,
        technical: TechnicalIndicators,
        fibo: FibonacciLevels,
        macro: MacroRegime
    ) -> RiskAudit:
        """Audits the quantitative profile and generates disciplined execution boundaries."""
        notes = []

        # 1. Mandate Checks
        sharpe_check = quant_factors.sharpe_ratio >= self.min_sharpe
        if sharpe_check:
            notes.append(f"PASS: Sharpe ratio ({quant_factors.sharpe_ratio}) meets institutional threshold (>= {self.min_sharpe}).")
        else:
            notes.append(f"FLAG: Sharpe ratio ({quant_factors.sharpe_ratio}) below target ({self.min_sharpe}).")

        drawdown_check = abs(quant_factors.max_drawdown) <= self.max_drawdown_limit
        if drawdown_check:
            notes.append(f"PASS: Historical peak-to-trough drawdown ({abs(quant_factors.max_drawdown)*100:.1f}%) within policy limit (<= {self.max_drawdown_limit*100:.0f}%).")
        else:
            notes.append(f"CAUTION: Max drawdown ({abs(quant_factors.max_drawdown)*100:.1f}%) breaches policy ceiling ({self.max_drawdown_limit*100:.0f}%).")

        var_check = quant_factors.daily_var_95 <= self.var_limit
        if var_check:
            notes.append(f"PASS: Daily 95% VaR ({quant_factors.daily_var_95*100:.2f}%) within tail-risk capacity (<= {self.var_limit*100:.1f}%).")
        else:
            notes.append(f"CAUTION: Tail risk daily VaR ({quant_factors.daily_var_95*100:.2f}%) exceeds standard risk limit.")

        # 2. Position Sizing
        # Volatility Targeting: Size = TargetVol / AssetVol
        asset_vol = max(quant_factors.annualized_volatility, 0.05)
        vol_size = float(np.clip(self.target_annual_vol / asset_vol, 0.02, self.max_allocation_cap))

        # Half-Kelly Criterion: f* = (p * b - (1-p)) / b * 0.5
        p = float(np.clip(quant_factors.win_rate, 0.35, 0.75))
        b = float(np.clip(quant_factors.profit_factor, 0.8, 3.5))
        raw_kelly = (p * b - (1.0 - p)) / b
        fractional_kelly = float(np.clip(raw_kelly * 0.5, 0.01, self.max_allocation_cap))

        recommended_allocation = min(vol_size, fractional_kelly, self.max_allocation_cap)

        # 3. Dynamic Trade Plan & Risk-Reward Execution
        current_price = technical.current_price
        atr = max(technical.atr_14, current_price * 0.01)

        # Stop loss anchored by ATR and Fibonacci support
        atr_stop_distance = 1.8 * atr
        fibo_support_distance = current_price - fibo.nearest_support

        if 0 < fibo_support_distance < (2.5 * atr):
            stop_loss_price = round(fibo.nearest_support - (0.2 * atr), 2)
        else:
            stop_loss_price = round(current_price - atr_stop_distance, 2)

        stop_loss_price = max(stop_loss_price, round(current_price * 0.85, 2))
        risk_distance = max(current_price - stop_loss_price, 0.01)
        stop_loss_pct = (risk_distance / current_price) * 100.0

        # Take Profit Targets
        tp1 = round(current_price + (1.618 * risk_distance), 2)
        tp2 = round(current_price + (2.618 * risk_distance), 2)
        rr_ratio = round((tp1 - current_price) / risk_distance, 2)

        # Verdict
        if sharpe_check and drawdown_check and var_check and quant_factors.sharpe_ratio >= 1.0:
            verdict = RiskAuditVerdict.APPROVED
            mandate_passed = True
            notes.append("AUDIT VERDICT: Fully APPROVED for institutional capital deployment.")
        elif quant_factors.sharpe_ratio > 0.3 and abs(quant_factors.max_drawdown) < 0.38:
            verdict = RiskAuditVerdict.APPROVED_WITH_CONDITIONS
            mandate_passed = True
            notes.append("AUDIT VERDICT: APPROVED WITH CONDITIONS - Enforce strict 50% reduced position sizing.")
            recommended_allocation *= 0.70
        else:
            verdict = RiskAuditVerdict.REJECTED
            mandate_passed = False
            notes.append("AUDIT VERDICT: REJECTED - Risk-adjusted returns fail fiduciary risk thresholds.")
            recommended_allocation = 0.0

        return RiskAudit(
            verdict=verdict,
            mandate_passed=mandate_passed,
            sharpe_check=sharpe_check,
            drawdown_check=drawdown_check,
            var_check=var_check,
            max_recommended_allocation=round(recommended_allocation, 4),
            volatility_target_size=round(vol_size, 4),
            fractional_kelly_size=round(fractional_kelly, 4),
            suggested_stop_loss_pct=round(stop_loss_pct, 2),
            suggested_stop_loss_price=round(stop_loss_price, 2),
            suggested_take_profit_1=round(tp1, 2),
            suggested_take_profit_2=round(tp2, 2),
            risk_reward_ratio=round(rr_ratio, 2),
            audit_notes=notes,
        )
