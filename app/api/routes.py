from fastapi import APIRouter, Query
from typing import Optional
from app.services.fund_analysis_service import analyze_funds, analyze_funds_with_benchmark
from app.services.smart_advisor import get_smart_recommendations

router = APIRouter()


@router.get("/")
def root():
    """Root endpoint."""
    return {"message": "OK"}


@router.get("/top5smallcap")
def get_top5_smallcap():
    """Get all small cap funds with analysis (sorted by performance)."""
    return analyze_funds()


@router.get("/top5smallcap-benchmark")
def get_top5_smallcap_with_benchmark():
    """Get all small cap funds with Nifty 50 benchmark analysis and recommendations (sorted by alpha)."""
    return {
        "funds": analyze_funds_with_benchmark(),
        "benchmark": "Nifty 50",
        "analysis_note": "All small cap direct growth funds are analyzed against Nifty 50 benchmark. Alpha shows excess returns, Beta shows volatility relative to market, Information Ratio shows risk-adjusted outperformance.",
        "recommendation_guide": {
            "STRONG BUY": "Excellent performance with low risk - suitable for aggressive investors",
            "BUY": "Good performance with acceptable risk - suitable for moderate to aggressive investors", 
            "HOLD": "Mixed performance - suitable for conservative to moderate investors",
            "AVOID": "Poor risk-adjusted returns - not recommended"
        }
    }


@router.get("/smart-advisor")
def get_smart_investment_advice(
    risk_tolerance: str = Query(default="moderate", description="Risk tolerance: conservative, moderate, aggressive"),
    investment_horizon: str = Query(default="long_term", description="Investment horizon: short_term, medium_term, long_term"),
    min_alpha: float = Query(default=0.0, description="Minimum alpha percentage required"),
    max_volatility: Optional[float] = Query(default=None, description="Maximum acceptable volatility percentage")
):
    """
    Smart advisor for Small Cap Direct Funds with personalized recommendations.
    
    Analyzes funds against Nifty 50 benchmark and provides:
    - Personalized fund recommendations based on risk profile
    - Portfolio allocation suggestions
    - Investment strategy guidance
    - Risk warnings and market outlook
    """
    return get_smart_recommendations(
        risk_tolerance=risk_tolerance,
        investment_horizon=investment_horizon,
        min_alpha=min_alpha,
        max_volatility=max_volatility
    )
