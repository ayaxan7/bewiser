from typing import List, Dict, Any, Optional
from app.services.fund_analysis_service import analyze_funds_with_benchmark


def get_smart_recommendations(
    risk_tolerance: str = "moderate",
    investment_horizon: str = "long_term",
    min_alpha: float = 0.0,
    max_volatility: Optional[float] = None
) -> Dict[str, Any]:
    """
    Smart advisor function that provides personalized fund recommendations.
    
    Args:
        risk_tolerance: "conservative", "moderate", "aggressive"
        investment_horizon: "short_term", "medium_term", "long_term"
        min_alpha: Minimum alpha required (default 0%)
        max_volatility: Maximum acceptable volatility % (optional)
    """
    
    # Get all funds with benchmark analysis
    funds = analyze_funds_with_benchmark()
    
    # Filter based on criteria
    filtered_funds = []
    
    for fund in funds:
        # Alpha filter
        alpha = fund.get('alpha_pct', 0)
        if alpha < min_alpha:
            continue
            
        # Volatility filter
        volatility = fund.get('volatility_pct', 999)
        if max_volatility and volatility and volatility > max_volatility:
            continue
            
        # Risk tolerance based filtering
        sharpe = fund.get('sharpe_ratio', 0) or 0
        info_ratio = fund.get('information_ratio', 0) or 0
        max_dd = abs(fund.get('max_drawdown_pct', 0) or 0)
        
        risk_score = _calculate_risk_score(sharpe, info_ratio, max_dd, volatility)
        
        if risk_tolerance == "conservative" and risk_score > 6:
            continue
        elif risk_tolerance == "moderate" and risk_score > 8:
            continue
        # Aggressive investors accept all risk levels
        
        fund['risk_score'] = risk_score
        filtered_funds.append(fund)
    
    # Sort by recommendation quality
    filtered_funds.sort(
        key=lambda x: (
            x.get('alpha_pct', -999),
            x.get('information_ratio', -999),
            -x.get('risk_score', 999)
        ),
        reverse=True
    )
    
    # Generate recommendations
    recommendations = _generate_investment_recommendations(
        filtered_funds, risk_tolerance, investment_horizon
    )
    
    return {
        "recommended_funds": filtered_funds[:3],  # Top 3 recommendations
        "analysis_summary": _generate_analysis_summary(filtered_funds),
        "investment_strategy": recommendations,
        "portfolio_allocation": _suggest_portfolio_allocation(filtered_funds[:3], risk_tolerance),
        "market_outlook": _generate_market_outlook(),
        "risk_warnings": _generate_risk_warnings(filtered_funds[:3]),
        "filters_applied": {
            "risk_tolerance": risk_tolerance,
            "investment_horizon": investment_horizon,
            "min_alpha_pct": min_alpha,
            "max_volatility_pct": max_volatility
        }
    }


def _calculate_risk_score(sharpe: float, info_ratio: float, max_dd: float, volatility: float) -> int:
    """Calculate a risk score from 1-10 (higher = riskier)."""
    score = 5  # Base score
    
    # Sharpe ratio adjustment
    if sharpe > 1.5:
        score -= 2
    elif sharpe > 1:
        score -= 1
    elif sharpe < 0.5:
        score += 1
    
    # Information ratio adjustment
    if info_ratio > 0.5:
        score -= 1
    elif info_ratio < 0:
        score += 2
    
    # Max drawdown adjustment
    if max_dd > 30:
        score += 3
    elif max_dd > 20:
        score += 2
    elif max_dd > 15:
        score += 1
    elif max_dd < 10:
        score -= 1
    
    # Volatility adjustment
    if volatility:
        if volatility > 25:
            score += 2
        elif volatility > 20:
            score += 1
        elif volatility < 15:
            score -= 1
    
    return max(1, min(10, score))


def _generate_investment_recommendations(
    funds: List[Dict[str, Any]], 
    risk_tolerance: str, 
    investment_horizon: str
) -> Dict[str, str]:
    """Generate personalized investment recommendations."""
    
    if not funds:
        return {
            "primary_recommendation": "No funds meet your criteria. Consider relaxing your filters.",
            "strategy": "Wait for better market conditions or consider broader market index funds."
        }
    
    top_fund = funds[0]
    alpha = top_fund.get('alpha_pct', 0)
    volatility = top_fund.get('volatility_pct', 0)
    
    recommendations = {}
    
    if risk_tolerance == "conservative":
        recommendations["primary_recommendation"] = (
            f"Consider {top_fund['fund_name']} as your primary choice. "
            f"With {alpha}% alpha and {volatility}% volatility, it offers good risk-adjusted returns."
        )
        recommendations["strategy"] = (
            "Start with a small allocation (10-15%) and gradually increase based on performance. "
            "Focus on SIP investments to reduce timing risk."
        )
    
    elif risk_tolerance == "moderate":
        if len(funds) >= 2:
            recommendations["primary_recommendation"] = (
                f"Split your investment between {top_fund['fund_name']} (60%) and "
                f"{funds[1]['fund_name']} (40%) for diversification."
            )
        else:
            recommendations["primary_recommendation"] = (
                f"Invest primarily in {top_fund['fund_name']} which shows {alpha}% alpha "
                f"against Nifty 50 benchmark."
            )
        recommendations["strategy"] = (
            "Use SIP for 70% of investment and lump sum for 30% during market corrections. "
            "Review performance quarterly."
        )
    
    else:  # aggressive
        recommendations["primary_recommendation"] = (
            f"Maximize allocation to {top_fund['fund_name']} given its strong {alpha}% alpha. "
            f"Consider up to 25-30% of your equity portfolio in small cap funds."
        )
        recommendations["strategy"] = (
            "Use market volatility to your advantage with systematic investments. "
            "Consider increasing allocation during market downturns."
        )
    
    # Investment horizon adjustments
    if investment_horizon == "short_term":
        recommendations["horizon_note"] = (
            "WARNING: Small cap funds are not suitable for short-term investments (< 3 years). "
            "Consider debt funds or large cap funds for short-term goals."
        )
    elif investment_horizon == "medium_term":
        recommendations["horizon_note"] = (
            "Medium-term investment (3-7 years) suitable. Monitor closely for the first 2 years."
        )
    else:
        recommendations["horizon_note"] = (
            "Excellent choice for long-term wealth creation (7+ years). "
            "Small cap funds historically outperform in long-term horizons."
        )
    
    return recommendations


def _generate_analysis_summary(funds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary analysis of the fund selection."""
    if not funds:
        return {"message": "No funds meet your criteria"}
    
    avg_alpha = sum(f.get('alpha_pct', 0) for f in funds[:3]) / min(len(funds), 3)
    avg_volatility = sum(f.get('volatility_pct', 0) or 0 for f in funds[:3]) / min(len(funds), 3)
    avg_sharpe = sum((f.get('sharpe_ratio') or 0) for f in funds[:3]) / min(len(funds), 3)
    
    positive_alpha_funds = sum(1 for f in funds if f.get('alpha_pct', 0) > 0)
    
    return {
        "total_funds_analyzed": len(funds),
        "funds_with_positive_alpha": positive_alpha_funds,
        "average_alpha_pct": round(avg_alpha, 2),
        "average_volatility_pct": round(avg_volatility, 2),
        "average_sharpe_ratio": round(avg_sharpe, 2),
        "market_outperformance": f"{positive_alpha_funds}/{len(funds)} funds beat Nifty 50"
    }


def _suggest_portfolio_allocation(
    funds: List[Dict[str, Any]], 
    risk_tolerance: str
) -> Dict[str, Any]:
    """Suggest portfolio allocation based on risk tolerance."""
    if not funds:
        return {"allocation": "No suitable funds found"}
    
    allocations = {}
    
    if risk_tolerance == "conservative":
        allocations = {
            "small_cap_funds": "10-15%",
            "large_cap_funds": "40-50%",
            "debt_funds": "35-50%",
            "recommendation": "Limited small cap exposure with focus on stability"
        }
    elif risk_tolerance == "moderate":
        allocations = {
            "small_cap_funds": "20-25%",
            "large_cap_funds": "35-45%",
            "mid_cap_funds": "10-15%",
            "debt_funds": "20-30%",
            "recommendation": "Balanced approach with moderate small cap exposure"
        }
    else:  # aggressive
        allocations = {
            "small_cap_funds": "25-35%",
            "large_cap_funds": "25-35%",
            "mid_cap_funds": "15-25%",
            "debt_funds": "10-20%",
            "recommendation": "Growth-focused with significant small cap allocation"
        }
    
    if funds:
        allocations["top_fund_suggestion"] = f"Primary allocation: {funds[0]['fund_name']}"
        if len(funds) > 1:
            allocations["secondary_fund"] = f"Secondary option: {funds[1]['fund_name']}"
    
    return allocations


def _generate_market_outlook() -> str:
    """Generate market outlook for small cap funds."""
    return (
        "Small cap funds typically outperform during economic expansion phases but can be "
        "highly volatile during market downturns. Current market conditions favor long-term "
        "investors with high risk tolerance. Consider market timing and economic cycles "
        "when making investment decisions."
    )


def _generate_risk_warnings(funds: List[Dict[str, Any]]) -> List[str]:
    """Generate risk warnings based on fund analysis."""
    warnings = [
        "Small cap funds are subject to high volatility and market risk",
        "Past performance does not guarantee future results",
        "Investments are subject to market risks - read all scheme documents carefully"
    ]
    
    if funds:
        avg_volatility = sum(f.get('volatility_pct', 0) or 0 for f in funds) / len(funds)
        if avg_volatility > 25:
            warnings.append(f"Selected funds show high volatility (avg {avg_volatility:.1f}%) - suitable only for high-risk investors")
        
        negative_alpha_funds = [f for f in funds if f.get('alpha_pct', 0) < 0]
        if negative_alpha_funds:
            warnings.append(f"{len(negative_alpha_funds)} recommended funds currently underperform benchmark")
    
    return warnings
