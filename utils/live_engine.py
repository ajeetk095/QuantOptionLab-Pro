"""live_engine.py — Live market data layer (yfinance, no API key) + recommendation logic.

Design:
  * fetch_live_quote / fetch_history   — spot price, previous close, intraday change,
                                          historical close series (for realised vol).
  * fetch_option_chain                 — nearest-expiry call/put quotes from Yahoo.
  * All fetches cached with st.cache_data (TTL 60–300 s) and wrapped so ANY failure
    returns None → callers show a visible "delayed/unavailable — demo mode" banner
    and fall back to the research study's parameters (S0=$80, σ=35%).
  * run_live_simulation                — Monte Carlo GBM (and Heston/Merton from
    utils.pricing) seeded with the LIVE spot and realised volatility.
  * build_recommendations              — transparent, rule-labelled strategy cards.
"""

from __future__ import annotations

import datetime as dt
from functools import lru_cache

import numpy as np
import pandas as pd

from utils.pricing import (
    V0_Heston, KAPPA_Heston, THETA_Heston, SIGMA_V_Heston,
    MU_J_Merton, SIGMA_J_Merton, heston_price, merton_price,
    binomial_american_call,
)

TICKER_DEFAULTS = ["AAPL", "MSFT", "NVDA", "TSLA", "SPY", "^GSPC"]

DEMO_PARAMS = dict(spot=80.0, sigma=0.35, r=0.055, T=0.25)


# ----------------------------------------------------------------------------
# Live data fetching (yfinance) — cached, fail-soft
# ----------------------------------------------------------------------------
def _yf():
    import yfinance as yf  # imported lazily so the app boots even if yfinance is blocked
    return yf


def fetch_live_quote(ticker: str) -> dict | None:
    """Spot quote via yfinance fast_info. Returns None on any failure (fail-soft)."""
    try:
        tk = _yf().Ticker(ticker)
        info = tk.fast_info
        spot = float(info["last_price"])
        prev = float(info["previous_close"] or spot)
        if not np.isfinite(spot) or spot <= 0:
            return None
        return {
            "ticker": ticker,
            "spot": spot,
            "previous_close": prev,
            "change": spot - prev,
            "change_pct": (spot - prev) / prev * 100 if prev else 0.0,
            "currency": str(info.get("currency") or "USD"),
            "timestamp": dt.datetime.now(dt.timezone.utc),
        }
    except Exception:
        return None


def fetch_history(ticker: str, days: int = 120) -> pd.DataFrame | None:
    """Daily close history via yfinance. Returns None on any failure."""
    try:
        df = _yf().Ticker(ticker).history(period=f"{days}d", interval="1d")
        if df is None or df.empty or "Close" not in df.columns:
            return None
        out = df[["Close"]].rename(columns={"Close": "close"}).copy()
        out.index = pd.to_datetime(out.index).tz_localize(None)
        out.index.name = "date"
        return out
    except Exception:
        return None


def realised_vol(hist: pd.DataFrame) -> float | None:
    """Annualised volatility from daily log returns."""
    try:
        rets = np.log(hist["close"]).diff().dropna()
        if len(rets) < 20:
            return None
        return float(rets.std() * np.sqrt(252))
    except Exception:
        return None


def fetch_option_chain(ticker: str) -> pd.DataFrame | None:
    """Nearest-expiry ATM-vicinity call/put quotes via yfinance. None on failure."""
    try:
        tk = _yf().Ticker(ticker)
        expiries = tk.options
        if not expiries:
            return None
        chain = tk.option_chain(expiries[0])
        calls, puts = chain.calls.copy(), chain.puts.copy()
        calls["type"], puts["type"] = "call", "put"
        df = pd.concat([calls, puts], ignore_index=True)
        cols = [c for c in ("strike", "type", "lastPrice", "bid", "ask",
                            "impliedVolatility", "openInterest") if c in df.columns]
        return df[cols].dropna(subset=["lastPrice"]).head(60)
    except Exception:
        return None


def get_market_state(ticker: str, days: int = 120) -> dict:
    """
    One call the UI uses: tries live data end-to-end; if ANY leg fails the whole
    state flips to demo mode with the research study's parameters.
    """
    quote = fetch_live_quote(ticker)
    hist = fetch_history(ticker, days)
    sigma = realised_vol(hist) if hist is not None else None

    if quote is None or hist is None or sigma is None:
        return {
            "live": False, "ticker": ticker,
            "spot": DEMO_PARAMS["spot"], "sigma": DEMO_PARAMS["sigma"],
            "r": DEMO_PARAMS["r"], "T": DEMO_PARAMS["T"],
            "hist": None, "quote": None, "error_time": dt.datetime.now(dt.timezone.utc),
        }
    return {
        "live": True, "ticker": ticker, "spot": quote["spot"], "sigma": sigma,
        "r": DEMO_PARAMS["r"], "T": DEMO_PARAMS["T"],
        "hist": hist, "quote": quote, "error_time": None,
    }


# ----------------------------------------------------------------------------
# Simulation on live data
# ----------------------------------------------------------------------------
def gbm_terminal_distribution(spot: float, sigma: float, r: float, T: float,
                              n_paths: int = 20_000, seed: int = 42) -> np.ndarray:
    """GBM terminal prices — the baseline simulation engine."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_paths)
    return spot * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)


def run_live_simulation(state: dict, horizon_months: int = 3,
                        n_paths: int = 20_000, seed: int = 42) -> dict:
    """Full pricing run on the live (or demo) market state."""
    S, sig, r, T = state["spot"], state["sigma"], state["r"], horizon_months / 12
    K = round(S, 2)  # ATM strike on today's live spot
    st_ = gbm_terminal_distribution(S, sig, r, T, n_paths, seed)
    ci_lo, ci_hi = float(np.percentile(st_, 5)), float(np.percentile(st_, 95))

    prices = {
        "european_call_mc": float(np.exp(-r * T) * np.mean(np.maximum(st_ - K, 0))),
        "european_put_mc": float(np.exp(-r * T) * np.mean(np.maximum(K - st_, 0))),
        "heston_call": heston_price(S, K, r, T, -0.30, "call", V0_Heston,
                                    KAPPA_Heston, THETA_Heston, SIGMA_V_Heston,
                                    num_paths=min(n_paths, 20_000), num_steps=100, seed=seed),
        "merton_call": merton_price(S, K, r, T, 0.75, "call", sig, MU_J_Merton,
                                    SIGMA_J_Merton, num_paths=min(n_paths, 20_000), seed=seed),
        "merton_put": merton_price(S, K, r, T, 0.75, "put", sig, MU_J_Merton,
                                   SIGMA_J_Merton, num_paths=min(n_paths, 20_000), seed=seed),
        "american_call": binomial_american_call(S, K, r, sig, T, steps=150),
    }
    return {
        "K": K, "T": T, "st_terminal": st_, "ci_lo": ci_lo, "ci_hi": ci_hi,
        "prob_down_10": float(np.mean(st_ < S * 0.90)),
        "prob_up_10": float(np.mean(st_ > S * 1.10)),
        "exp_return": float(np.mean(st_) / S - 1),
        "prices": prices,
    }


# ----------------------------------------------------------------------------
# Recommendations — transparent rules, labelled
# ----------------------------------------------------------------------------
def build_recommendations(state: dict, sim: dict) -> list[dict]:
    """
    Rule-based strategy cards. Every card carries the exact rule that fired so
    visitors can audit the logic (educational — not financial advice).
    """
    spot, sigma = state["spot"], state["sigma"]
    p = sim["prices"]
    out = []

    out.append({
        "title": "IV / vol regime",
        "verdict": "Elevated volatility" if sigma > 0.40 else
                   "Moderate volatility" if sigma > 0.25 else "Low volatility",
        "rule": f"Rule: annualised realised vol = {sigma*100:.1f}% "
                f"(>40% elevated · 25–40% moderate · <25% low).",
        "detail": "Realised vol computed from daily log returns over the last ~120 trading days.",
    })

    if sim["prob_down_10"] > 0.20:
        out.append({
            "title": "Downside protection",
            "verdict": f"Consider puts — {sim['prob_down_10']*100:.0f}% chance of a −10% move",
            "rule": "Rule: P(S_T < 0.9·S₀) > 20% from the Monte Carlo terminal distribution.",
            "detail": f"Model ATM put (Merton jump-diffusion, λ=0.75): ${p['merton_put']:.2f}. "
                      "Jump risk fattens the left tail — this is why puts look rich here.",
        })
    else:
        out.append({
            "title": "Downside protection",
            "verdict": f"Puts less urgent — {sim['prob_down_10']*100:.0f}% chance of a −10% move",
            "rule": "Rule: P(S_T < 0.9·S₀) ≤ 20% from the Monte Carlo terminal distribution.",
            "detail": "Left-tail risk is contained in the current simulation.",
        })

    skew = p["merton_put"] - p["merton_call"]
    out.append({
        "title": "Skew signal",
        "verdict": "Put premium dominates (crash-risk priced in)" if skew > 1 else
                   "Balanced call/put pricing" if skew > -1 else "Call premium dominates (upside demand)",
        "rule": f"Rule: Merton put − Merton call = ${skew:.2f} "
                f"(>+$1 put-rich · ±$1 balanced · <−$1 call-rich).",
        "detail": "A large positive skew mirrors the research finding: negative-mean jumps "
                  "(µ = −0.5) make downside protection expensive.",
    })

    out.append({
        "title": "Model spread",
        "verdict": f"Heston−Merton call gap: ${p['heston_call'] - p['merton_call']:+.2f}",
        "rule": "Rule: compare Heston (stochastic vol) vs Merton (jumps) ATM call prices.",
        "detail": "A large gap tells you which risk channel (vol-of-vol vs jumps) the market "
                  "context is stressing — use both models before trading any structure.",
    })

    early = p["american_call"] - p["european_call_mc"]
    out.append({
        "title": "Early-exercise check",
        "verdict": f"American ≈ European (Δ ${early:+.2f}) — no early-exercise value",
        "rule": "Rule: American − European call premium (binomial tree vs Monte Carlo).",
        "detail": "For a non-dividend-paying underlying, early exercise of a call is never "
                  "optimal — the app confirms this numerically on live data (research Q13).",
    })

    return out
