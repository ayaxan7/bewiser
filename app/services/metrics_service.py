import pandas as pd
import numpy as np
from typing import Optional
from app.config.settings import RISK_FREE_RATE, TRADING_DAYS


def _annualize_vol(daily_returns: pd.Series) -> float:
    """Annualize volatility from daily returns."""
    return daily_returns.std() * np.sqrt(TRADING_DAYS)


def calculate_volatility(df: pd.DataFrame) -> Optional[float]:
    """Calculate annualized volatility."""
    if len(df) < 2:
        return None
    ret = df["nav"].pct_change().dropna()
    if ret.empty:
        return None
    return _annualize_vol(ret)


def calculate_sharpe(cagr: Optional[float], volatility: Optional[float]) -> Optional[float]:
    """Calculate Sharpe ratio."""
    if cagr is None or volatility is None or volatility == 0:
        return None
    return (cagr - RISK_FREE_RATE) / volatility


def calculate_max_drawdown(df: pd.DataFrame) -> Optional[float]:
    """Calculate maximum drawdown."""
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
