from typing import List, Dict, Any
from app.services.data_service import fetch_all_funds, fetch_nav_history
from app.services.metrics_service import (
    calculate_volatility, calculate_sharpe, calculate_max_drawdown,
    cagr_for_window, absolute_return_for_window, full_period_cagr
)
from app.services.benchmark_service import (
    fetch_nifty50_data, calculate_benchmark_metrics, 
    calculate_risk_adjusted_metrics, get_benchmark_recommendation
)
from app.utils.helpers import r


def analyze_funds_with_benchmark() -> List[Dict[str, Any]]:
    """Analyze top 5 small cap funds with Nifty 50 benchmark comparison."""
    top_funds = fetch_all_funds()
    results = []
    
    # Fetch Nifty 50 benchmark data
    nifty_data = fetch_nifty50_data()

    for fund in top_funds:
        code = fund["schemeCode"]
        df, name = fetch_nav_history(code)
        if df.empty:
            continue

        # Standard fund metrics
        vol = calculate_volatility(df)
        max_dd = calculate_max_drawdown(df)

        # Returns / CAGR metrics
        ret_3m = absolute_return_for_window(df, 90)
        ret_6m = absolute_return_for_window(df, 180)
        ret_1y = absolute_return_for_window(df, 365)

        cagr_all = full_period_cagr(df)
        cagr_1y = cagr_for_window(df, 1)
        cagr_2y = cagr_for_window(df, 2)
        cagr_3y = cagr_for_window(df, 3)
        cagr_5y = cagr_for_window(df, 5)

        sharpe = calculate_sharpe(cagr_3y if cagr_3y is not None else cagr_all, vol)

        # Benchmark comparison metrics
        benchmark_metrics = calculate_benchmark_metrics(df, nifty_data)
        risk_adjusted_metrics = calculate_risk_adjusted_metrics(df, nifty_data)
        
        # Generate recommendation
        combined_metrics = {
            **benchmark_metrics,
            **risk_adjusted_metrics,
            'sharpe_ratio': sharpe
        }
        recommendation = get_benchmark_recommendation(combined_metrics)

        fund_result = {
            "scheme_code": code,
            "fund_name": name,

            # Absolute (period) returns %
            "returns_3m_pct": r(ret_3m),
            "returns_6m_pct": r(ret_6m),
            "returns_1y_pct": r(ret_1y),

            # CAGR %
            "cagr_full_pct": r(cagr_all),
            "cagr_1y_pct": r(cagr_1y),
            "cagr_2y_pct": r(cagr_2y),
            "cagr_3y_pct": r(cagr_3y),
            "cagr_5y_pct": r(cagr_5y),

            # Risk metrics
            "volatility_pct": r(vol),
            "sharpe_ratio": round(sharpe, 2) if sharpe is not None else None,
            "max_drawdown_pct": r(max_dd),
            
            # Benchmark comparison metrics
            **benchmark_metrics,
            **risk_adjusted_metrics,
            
            # Investment recommendation
            "recommendation": recommendation
        }
        
        results.append(fund_result)

    # Sort by alpha, then information ratio, then Sharpe ratio
    results.sort(
        key=lambda x: (
            x.get("alpha_pct", -999),
            x.get("information_ratio", -999),
            x["sharpe_ratio"] if x["sharpe_ratio"] is not None else -999
        ),
        reverse=True
    )
    return results


def analyze_funds() -> List[Dict[str, Any]]:
    """Analyze top 5 small cap funds and return sorted results."""
    top_funds = fetch_all_funds()
    results = []

    for fund in top_funds:
        code = fund["schemeCode"]
        df, name = fetch_nav_history(code)
        if df.empty:
            continue

        # Risk metrics
        vol = calculate_volatility(df)
        max_dd = calculate_max_drawdown(df)

        # Returns / CAGR metrics
        # Absolute returns
        ret_3m = absolute_return_for_window(df, 90)
        ret_6m = absolute_return_for_window(df, 180)
        ret_1y = absolute_return_for_window(df, 365)

        # CAGR with rolling windows
        cagr_all = full_period_cagr(df)
        cagr_1y = cagr_for_window(df, 1)
        cagr_2y = cagr_for_window(df, 2)
        cagr_3y = cagr_for_window(df, 3)
        cagr_5y = cagr_for_window(df, 5)

        sharpe = calculate_sharpe(cagr_3y if cagr_3y is not None else cagr_all, vol)

        results.append({
            "scheme_code": code,
            "fund_name": name,

            # Absolute (period) returns %
            "returns_3m_pct": r(ret_3m),
            "returns_6m_pct": r(ret_6m),
            "returns_1y_pct": r(ret_1y),

            # CAGR %
            "cagr_full_pct": r(cagr_all),
            "cagr_1y_pct": r(cagr_1y),
            "cagr_2y_pct": r(cagr_2y),
            "cagr_3y_pct": r(cagr_3y),
            "cagr_5y_pct": r(cagr_5y),

            # Risk metrics
            "volatility_pct": r(vol),
            "sharpe_ratio": round(sharpe, 2) if sharpe is not None else None,
            "max_drawdown_pct": r(max_dd)
        })

    # Sort primarily by Sharpe (desc), then by 3Y CAGR (desc)
    results.sort(
        key=lambda x: (
            x["sharpe_ratio"] if x["sharpe_ratio"] is not None else -1e9,
            x["cagr_3y_pct"] if x["cagr_3y_pct"] is not None else -1e9
        ),
        reverse=True
    )
    return results
