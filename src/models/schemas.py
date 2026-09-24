from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ConvictionRating(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    REDUCE = "REDUCE"
    SELL = "SELL"


class RiskAuditVerdict(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    REJECTED = "REJECTED"


class MarketRegimeType(str, Enum):
    EXPANSION_RISK_ON = "EXPANSION_RISK_ON"
    LATE_CYCLE = "LATE_CYCLE"
    CONTRACTION_RISK_OFF = "CONTRACTION_RISK_OFF"
    RECOVERY = "RECOVERY"


class TechnicalIndicators(BaseModel):
    current_price: float
    ema_20: float
    ema_50: float
    ema_200: float
    rsi_14: float
    macd: float
    macd_signal: float
    macd_hist: float
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    atr_14: float
    trend_signal: str
    rsi_condition: str


class FibonacciLevels(BaseModel):
    swing_high: float
    swing_low: float
    trend_direction: str  # "UPTREND" or "DOWNTREND"
    level_0: float        # 0.0% (Current Extreme)
    level_236: float      # 23.6%
    level_382: float      # 38.2%
    level_500: float      # 50.0%
    level_618: float      # 61.8% (Golden Pocket)
    level_786: float      # 78.6%
    level_100: float      # 100.0% (Base)
    nearest_support: float
    nearest_resistance: float


class QuantFactors(BaseModel):
    ticker: str
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    beta_to_sp500: float
    alpha_annualized: float
    daily_var_95: float
    daily_cvar_95: float
    win_rate: float
    profit_factor: float


class MacroRegime(BaseModel):
    fed_funds_rate: float
    us_cpi_inflation: float
    yield_10y: float
    yield_2y: float
    yield_curve_spread: float
    is_yield_curve_inverted: bool
    vix_level: float
    vix_regime: str  # "LOW_VOLATILITY", "NORMAL_VOLATILITY", "HIGH_VOLATILITY_PANIC"
    macro_regime: MarketRegimeType
    macro_tailwinds: List[str]
    macro_headwinds: List[str]


class NewsSentimentItem(BaseModel):
    title: str
    source: str
    sentiment_score: float  # -1.0 to 1.0
    sentiment_label: str    # "BULLISH", "NEUTRAL", "BEARISH"
    relevance: float


class SentimentAnalysis(BaseModel):
    aggregate_score: float  # -1.0 to 1.0
    overall_sentiment: str  # "BULLISH", "MODERATELY_BULLISH", "NEUTRAL", "BEARISH"
    bullish_mentions: int
    bearish_mentions: int
    neutral_mentions: int
    key_themes: List[str]
    sentiment_price_divergence: str  # "CONVERGENT", "BULLISH_DIVERGENCE", "BEARISH_DIVERGENCE"


class RiskAudit(BaseModel):
    verdict: RiskAuditVerdict
    mandate_passed: bool
    sharpe_check: bool
    drawdown_check: bool
    var_check: bool
    max_recommended_allocation: float  # fraction of portfolio (e.g. 0.08)
    volatility_target_size: float
    fractional_kelly_size: float
    suggested_stop_loss_pct: float
    suggested_stop_loss_price: float
    suggested_take_profit_1: float
    suggested_take_profit_2: float
    risk_reward_ratio: float
    audit_notes: List[str]


class InvestmentThesis(BaseModel):
    ticker: str
    company_name: Optional[str] = None
    as_of_date: str
    conviction_rating: ConvictionRating
    confidence_score: float  # 0.0 to 100.0%
    price_target: float
    current_price: float
    expected_return_pct: float
    time_horizon: str
    executive_summary: str
    technical_analysis: TechnicalIndicators
    fibonacci_framework: FibonacciLevels
    quantitative_factors: QuantFactors
    macro_environment: MacroRegime
    sentiment_analysis: SentimentAnalysis
    risk_management: RiskAudit
    catalysts: List[str]
    primary_risks: List[str]
    actionable_trade_plan: Dict[str, float]


class AnalysisRequest(BaseModel):
    ticker: str = Field(default="NVDA", description="Equity or ETF ticker symbol")
    period: str = Field(default="1y", description="Historical data period: 6mo, 1y, 2y, 5y")
    benchmark: str = Field(default="^GSPC", description="Benchmark index for beta calculation")


class HealthResponse(BaseModel):
    status: str
    system: str
    version: str
    active_agents: List[str]
