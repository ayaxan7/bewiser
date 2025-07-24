from fastapi import FastAPI
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List
import json
import os
app = FastAPI(title="Small Cap Fund Advisor", version="1.0")

# =====================================
# CONFIGURATION
# =====================================
RISK_FREE_RATE = 0.07
TRADING_DAYS = 252

# =====================================
# HELPER FUNCTIONS
# =====================================

def fetch_all_funds():
    url = "https://api.mfapi.in/mf"
    response = requests.get(url)
    funds = response.json()
    filtered = [f for f in funds if f['schemeName'] 
            and "small cap" in f['schemeName'].lower()
            and "direct" in f['schemeName'].lower()
            and "growth" in f['schemeName'].lower()
            and "bonus" not in f['schemeName'].lower()
            and "dividend" not in f['schemeName'].lower()]
    return filtered[:5]

def fetch_nav_history(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    data = response.json()
    nav_data = data.get("data", [])
    df = pd.DataFrame(nav_data)
    if df.empty:
        return df, data.get("meta", {}).get("scheme_name", "Unknown Fund")
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['nav'] = df['nav'].astype(float)
    df = df.sort_values('date').reset_index(drop=True)
    return df, data.get("meta", {}).get("scheme_name", "Unknown Fund")

def calculate_cagr(df):
    start_value = df.iloc[0]['nav']
    end_value = df.iloc[-1]['nav']
    n_years = (df.iloc[-1]['date'] - df.iloc[0]['date']).days / 365.25
    return (end_value / start_value) ** (1 / n_years) - 1

def calculate_volatility(df):
    df['daily_return'] = df['nav'].pct_change()
    daily_std = df['daily_return'].std()
    return daily_std * np.sqrt(TRADING_DAYS)

def calculate_sharpe(cagr, volatility):
    return (cagr - RISK_FREE_RATE) / volatility if volatility else None

def calculate_max_drawdown(df):
    df['cum_max'] = df['nav'].cummax()
    df['drawdown'] = (df['nav'] - df['cum_max']) / df['cum_max']
    return df['drawdown'].min()

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
        code = fund['schemeCode']
        df, name = fetch_nav_history(code)
        if df.empty:
            continue

        cagr = calculate_cagr(df)
        vol = calculate_volatility(df)
        sharpe = calculate_sharpe(cagr, vol)
        max_dd = calculate_max_drawdown(df)

        results.append({
            "scheme_code": code,
            "fund_name": name,
            "cagr": round(cagr * 100, 2),
            "volatility": round(vol * 100, 2),
            "sharpe_ratio": round(sharpe, 2) if sharpe else None,
            "max_drawdown": round(max_dd * 100, 2)
        })

    results.sort(key=lambda x: x['sharpe_ratio'] if x['sharpe_ratio'] else 0, reverse=True)
    return results
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)