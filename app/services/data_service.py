import requests
import pandas as pd
from typing import Tuple, List, Dict, Any


def fetch_all_funds() -> List[Dict[str, Any]]:
    """Fetch and filter small cap direct growth funds."""
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
    return filtered[:33]


def fetch_nav_history(scheme_code: str) -> Tuple[pd.DataFrame, str]:
    """Fetch NAV history for a given scheme code."""
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
