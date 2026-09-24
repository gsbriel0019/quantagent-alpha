import pytest
from src.agents.thesis_synthesizer import ThesisSynthesizerAgent
from src.models.schemas import ConvictionRating, InvestmentThesis


def test_thesis_synthesizer_pipeline():
    synthesizer = ThesisSynthesizerAgent()
    thesis = synthesizer.run("NVDA", period="6mo")

    assert isinstance(thesis, InvestmentThesis)
    assert thesis.ticker == "NVDA"
    assert 0 <= thesis.confidence_score <= 100
    assert thesis.current_price > 0
    assert thesis.price_target > 0
    assert isinstance(thesis.conviction_rating, ConvictionRating)
    assert len(thesis.executive_summary) > 50
    assert len(thesis.catalysts) > 0
    assert len(thesis.primary_risks) > 0
    assert "entry_reference_price" in thesis.actionable_trade_plan
    assert "stop_loss_price" in thesis.actionable_trade_plan
    assert "take_profit_target_1" in thesis.actionable_trade_plan
