import pytest
from src.agents.risk_auditor_agent import RiskAuditorAgent
from src.models.schemas import (
    QuantFactors,
    TechnicalIndicators,
    FibonacciLevels,
    MacroRegime,
    MarketRegimeType,
    RiskAuditVerdict,
)


@pytest.fixture
def mock_models():
    factors = QuantFactors(
        ticker="NVDA",
        annualized_return=0.35,
        annualized_volatility=0.25,
        sharpe_ratio=1.22,
        sortino_ratio=1.65,
        calmar_ratio=1.40,
        max_drawdown=-0.18,
        beta_to_sp500=1.45,
        alpha_annualized=0.12,
        daily_var_95=0.024,
        daily_cvar_95=0.035,
        win_rate=0.56,
        profit_factor=1.45,
    )
    tech = TechnicalIndicators(
        current_price=120.0,
        ema_20=118.0,
        ema_50=114.0,
        ema_200=102.0,
        rsi_14=58.5,
        macd=1.2,
        macd_signal=0.8,
        macd_hist=0.4,
        bollinger_upper=126.0,
        bollinger_middle=117.0,
        bollinger_lower=108.0,
        atr_14=3.5,
        trend_signal="STRONG_BULLISH",
        rsi_condition="NEUTRAL",
    )
    fibo = FibonacciLevels(
        swing_high=130.0,
        swing_low=95.0,
        trend_direction="UPTREND",
        level_0=130.0,
        level_236=121.74,
        level_382=116.63,
        level_500=112.5,
        level_618=108.37,
        level_786=102.49,
        level_100=95.0,
        nearest_support=116.63,
        nearest_resistance=121.74,
    )
    macro = MacroRegime(
        fed_funds_rate=0.0525,
        us_cpi_inflation=0.029,
        yield_10y=0.0425,
        yield_2y=0.0405,
        yield_curve_spread=0.0020,
        is_yield_curve_inverted=False,
        vix_level=15.5,
        vix_regime="LOW_VOLATILITY",
        macro_regime=MarketRegimeType.EXPANSION_RISK_ON,
        macro_tailwinds=["Low volatility"],
        macro_headwinds=[],
    )
    return factors, tech, fibo, macro


def test_risk_auditor_approval(mock_models):
    factors, tech, fibo, macro = mock_models
    auditor = RiskAuditorAgent()
    audit = auditor.run(factors, tech, fibo, macro)

    assert audit.verdict == RiskAuditVerdict.APPROVED
    assert audit.mandate_passed is True
    assert audit.sharpe_check is True
    assert audit.drawdown_check is True
    assert audit.var_check is True
    assert 0 < audit.max_recommended_allocation <= 0.20
    assert audit.suggested_stop_loss_price < tech.current_price
    assert audit.suggested_take_profit_1 > tech.current_price
    assert audit.suggested_take_profit_2 > audit.suggested_take_profit_1
    assert audit.risk_reward_ratio >= 1.5
