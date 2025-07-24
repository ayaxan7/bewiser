from fastapi import FastAPI
import requests
import pandas as pd
import numpy as np
import os
from typing import Optional

app = FastAPI(title="Small Cap Fund Advisor", version="1.1")

# =====================================
# CONFIGURATION
# =====================================
RISK_FREE_RATE = 0.07   # 7%
TRADING_DAYS = 252

# =====================================
# DATA HELPERS
# =====================================

def fetch_all_funds():
    url = "https://api.mfapi.in/mf"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    funds = response.json()
    filtered = [
        f for f in funds
        if f.get("schemeName")
        and "small cap" in f["schemeName"].lower()
        and "direct" in f["schemeName"].lower()
        and "growth" in f["schemeName"].lower()
        and "bonus" not in f["schemeName"].lower()
        and "dividend" not in f["schemeName"].lower()
    ]
    return filtered[:5]

def fetch_nav_history(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    nav_data = data.get("data", [])
    df = pd.DataFrame(nav_data)
    if df.empty:
        return df, data.get("meta", {}).get("scheme_name", "Unknown Fund")

    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = df["nav"].astype(float)
    df = df.sort_values("date").reset_index(drop=True)
    return df, data.get("meta", {}).get("scheme_name", "Unknown Fund")

# =====================================
# METRIC CALCULATORS
# =====================================

def _annualize_vol(daily_returns: pd.Series) -> float:
    return daily_returns.std() * np.sqrt(TRADING_DAYS)

def calculate_volatility(df: pd.DataFrame) -> Optional[float]:
    if len(df) < 2:
        return None
    ret = df["nav"].pct_change().dropna()
    if ret.empty:
        return None
    return _annualize_vol(ret)

def calculate_sharpe(cagr: Optional[float], volatility: Optional[float]) -> Optional[float]:
    if cagr is None or volatility is None or volatility == 0:
        return None
    return (cagr - RISK_FREE_RATE) / volatility

def calculate_max_drawdown(df: pd.DataFrame) -> Optional[float]:
    if df.empty:
        return None
    cum_max = df["nav"].cummax()
    drawdown = df["nav"] / cum_max - 1.0
    return drawdown.min()

def cagr_for_window(df: pd.DataFrame, years: float) -> Optional[float]:
    """CAGR using only the last `years` of data (if available)."""
    if df.empty:
        return None
    end_date = df["date"].max()
    start_cutoff = end_date - pd.Timedelta(days=int(365.25 * years))
    window = df[df["date"] >= start_cutoff]
    if len(window) < 2:
        return None
    start_value = window.iloc[0]["nav"]
    end_value = window.iloc[-1]["nav"]
    n_years = (window.iloc[-1]["date"] - window.iloc[0]["date"]).days / 365.25
    if n_years <= 0:
        return None
    return (end_value / start_value) ** (1 / n_years) - 1

def absolute_return_for_window(df: pd.DataFrame, days: int) -> Optional[float]:
    """Simple absolute return over last `days` days."""
    if df.empty or days <= 0:
        return None
    end_date = df["date"].max()
    start_cutoff = end_date - pd.Timedelta(days=days)
    window = df[df["date"] >= start_cutoff]
    if len(window) < 2:
        return None
    start_value = window.iloc[0]["nav"]
    end_value = window.iloc[-1]["nav"]
    return (end_value / start_value) - 1.0

def full_period_cagr(df: pd.DataFrame) -> Optional[float]:
    """CAGR from first to last available NAV."""
    if len(df) < 2:
        return None
    start_value = df.iloc[0]["nav"]
    end_value = df.iloc[-1]["nav"]
    n_years = (df.iloc[-1]["date"] - df.iloc[0]["date"]).days / 365.25
    if n_years <= 0:
        return None
    return (end_value / start_value) ** (1 / n_years) - 1

# Safe rounding helper
def r(x, mult=100, nd=2):
    return round(x * mult, nd) if x is not None else None

# =====================================
# API ENDPOINTS
# =====================================

@app.get("/")
def root():
    return {"message": "OK"}

@app.get("/top5smallcap")
def get_top5_smallcap():
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
        ret_3m  = absolute_return_for_window(df, 90)
        ret_6m  = absolute_return_for_window(df, 180)
        ret_1y  = absolute_return_for_window(df, 365)

        # CAGR with rolling windows
        cagr_all = full_period_cagr(df)
        cagr_1y  = cagr_for_window(df, 1)
        cagr_2y  = cagr_for_window(df, 2)
        cagr_3y  = cagr_for_window(df, 3)
        cagr_5y  = cagr_for_window(df, 5)

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
