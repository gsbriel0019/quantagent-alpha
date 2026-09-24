import pytest
import numpy as np
import pandas as pd
from src.agents.quant_factor_agent import QuantFactorAgent


@pytest.fixture
def asset_and_bench():
    np.random.seed(100)
    dates = pd.date_range("2025-01-01", periods=120, freq="B")
    ret_asset = np.random.normal(0.001, 0.02, 120)
    ret_bench = np.random.normal(0.0005, 0.012, 120)

    p_asset = 150.0 * np.exp(np.cumsum(ret_asset))
    p_bench = 5000.0 * np.exp(np.cumsum(ret_bench))

    df_asset = pd.DataFrame(
        {"Open": p_asset, "High": p_asset * 1.01, "Low": p_asset * 0.99, "Close": p_asset, "Volume": 1000},
        index=dates
    )
    df_bench = pd.DataFrame(
        {"Open": p_bench, "High": p_bench * 1.005, "Low": p_bench * 0.995, "Close": p_bench, "Volume": 5000},
        index=dates
    )
    return df_asset, df_bench


def test_quant_factor_agent_metrics(asset_and_bench):
    df_asset, df_bench = asset_and_bench
    agent = QuantFactorAgent(risk_free_rate=0.045)
    factors, tech, fibo = agent.run("NVDA", df_asset, df_bench)

    assert factors.ticker == "NVDA"
    assert factors.annualized_volatility > 0
    assert -1.0 <= factors.max_drawdown <= 0.0
    assert factors.beta_to_sp500 != 0
    assert factors.daily_var_95 > 0
    assert factors.daily_cvar_95 >= factors.daily_var_95
    assert 0.0 <= factors.win_rate <= 1.0
    assert factors.profit_factor > 0

    assert tech.current_price > 0
    assert fibo.swing_high >= fibo.swing_low
