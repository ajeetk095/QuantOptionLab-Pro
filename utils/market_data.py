"""market_data.py — free, key-less market data with graceful demo fallback."""

from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests

DATA_SOURCE_NOTE = (
    "Data source: free public endpoints (Stooq CSV — no API key). Cached for 5 minutes. "
    "When the network blocks external calls, the page switches to Demo Mode using the "
    "research study's parameters (S0 = $80, sigma = 35%) so the app always remains usable."
)

STOOQ_URL = "https://stooq.com/q/d/l/"


def fetch_daily_history(ticker: str, days: int = 120) -> pd.DataFrame | None:
    """Fetch daily close prices from Stooq (free, no key). Returns None on failure."""
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=int(days * 1.6) + 10)
    params = {
        "s": ticker.lower(),
        "d1": start.strftime("%Y%m%d"),
        "d2": end.strftime("%Y%m%d"),
        "i": "d",
    }
    try:
        resp = requests.get(STOOQ_URL, params=params, timeout=8,
                            headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        if df.empty or "Close" not in df.columns:
            return None
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date").sort_index()
        df = df.tail(days)
        df.index.name = "date"
        return df[["Close"]].rename(columns={"Close": "close"})
    except Exception:
        return None


def fetch_spot_price(ticker: str) -> float | None:
    """Latest available price (last close) — free fallback spot estimate."""
    hist = fetch_daily_history(ticker, 10)
    if hist is None or hist.empty:
        return None
    return float(hist["close"].iloc[-1])


def demo_history(days: int = 120, s0: float = 80.0, sigma: float = 0.35,
                 seed: int = 42) -> pd.DataFrame:
    """Deterministic GBM series using the research study's parameters."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=datetime.now(timezone.utc).date(), periods=days)
    rets = rng.normal(0.0003, sigma / np.sqrt(252), days)
    px = s0 * np.exp(np.cumsum(rets))
    return pd.DataFrame({"close": px}, index=dates.rename("date"))
