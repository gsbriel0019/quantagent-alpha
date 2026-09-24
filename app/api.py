import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from src.agents.thesis_synthesizer import ThesisSynthesizerAgent
from src.data.macro_data import MacroDataLoader
from src.reporting.investment_memo import InvestmentMemoGenerator
from src.models.schemas import InvestmentThesis, HealthResponse, MacroRegime

logger = logging.getLogger("quantagent.api")

app = FastAPI(
    title="QuantAgent-Alpha Institutional API",
    description="Multi-Agent Quantitative Intelligence, Macro Sentiment & Investment Thesis Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

synthesizer = ThesisSynthesizerAgent()
macro_loader = MacroDataLoader()


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to QuantAgent-Alpha API",
        "author": "Gabriel Proaño",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="HEALTHY",
        system="QuantAgent-Alpha",
        version="1.0.0",
        active_agents=[
            "QuantFactorAgent",
            "MacroSentimentAgent",
            "RiskAuditorAgent",
            "ThesisSynthesizerAgent",
        ],
    )


@app.get("/analyze/{ticker}", response_model=InvestmentThesis, tags=["Analysis"])
def analyze_ticker(
    ticker: str,
    period: str = Query("1y", description="Time period: 6mo, 1y, 2y, 5y"),
    benchmark: str = Query("^GSPC", description="Benchmark index for beta calculation"),
):
    """Executes complete multi-agent pipeline and returns an institutional Investment Thesis."""
    try:
        thesis = synthesizer.timed_run(
            ticker=ticker,
            benchmark=benchmark,
            period=period
        )
        return thesis
    except Exception as e:
        logger.error(f"Analysis failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/thesis/memo/{ticker}", tags=["Analysis"])
def get_investment_memo(
    ticker: str,
    period: str = Query("1y", description="Time period: 6mo, 1y, 2y, 5y"),
):
    """Returns the formatted Markdown Executive Investment Memorandum."""
    try:
        thesis = synthesizer.timed_run(ticker=ticker, period=period)
        markdown_memo = InvestmentMemoGenerator.generate_markdown_memo(thesis)
        return {
            "ticker": ticker.upper(),
            "as_of_date": thesis.as_of_date,
            "conviction": thesis.conviction_rating.value,
            "memo_markdown": markdown_memo,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/macro/regime", tags=["Macro"])
def get_macro_environment():
    """Returns current macroeconomic factor levels and yield curve metrics."""
    try:
        macro = macro_loader.fetch_live_macro_indicators()
        return macro
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
