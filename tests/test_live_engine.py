"""tests/test_live_engine.py — tests for the live-data layer and fallback paths."""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from utils import live_engine as le
from utils.live_engine import (
    DEMO_PARAMS, build_recommendations, get_market_state, gbm_terminal_distribution,
    realised_vol, run_live_simulation,
)


def _fake_quote():
    return {"ticker": "AAPL", "spot": 180.0, "previous_close": 178.0, "change": 2.0,
            "change_pct": 1.12, "currency": "USD",
            "timestamp": pd.Timestamp.utcnow().to_pydatetime()}


def _fake_hist():
    rng = np.random.default_rng(7)
    idx = pd.bdate_range(end="2026-11-13", periods=120)
    px = 180 * np.exp(np.cumsum(rng.normal(0.0003, 0.02, 120)))
    return pd.DataFrame({"close": px}, index=idx.rename("date"))


def test_gbm_terminal_distribution_stats():
    st_ = gbm_terminal_distribution(100, 0.30, 0.05, 1.0, n_paths=50_000, seed=1)
    # E[S_T] = S0 * e^{rT}
    assert abs(st_.mean() / (100 * np.exp(0.05))) - 1 < 0.02
    assert st_.min() > 0


def test_realised_vol_positive():
    v = realised_vol(_fake_hist())
    assert v is not None and 0.0 < v < 2.0


def test_get_market_state_fallback_when_yf_fails():
    """If every yfinance call raises, get_market_state must return demo mode."""
    with patch.object(le, "fetch_live_quote", return_value=None), \
         patch.object(le, "fetch_history", return_value=None):
        state = get_market_state("AAPL")
    assert state["live"] is False
    assert state["spot"] == DEMO_PARAMS["spot"]
    assert state["sigma"] == DEMO_PARAMS["sigma"]
    assert state["hist"] is None


def test_get_market_state_live_success():
    with patch.object(le, "fetch_live_quote", return_value=_fake_quote()), \
         patch.object(le, "fetch_history", return_value=_fake_hist()):
        state = get_market_state("AAPL")
    assert state["live"] is True
    assert state["spot"] == 180.0
    assert state["sigma"] > 0
    assert state["hist"] is not None


def test_run_live_simulation_on_demo_state():
    state = get_market_state("AAPL")  # forces demo mode in sandbox
    sim = run_live_simulation(state, n_paths=10_000, seed=42)
    assert sim["prices"]["european_call_mc"] > 0
    assert sim["prices"]["european_put_mc"] > 0
    assert 0.0 <= sim["prob_down_10"] <= 1.0


def test_recommendations_carry_rules():
    state = get_market_state("AAPL")
    sim = run_live_simulation(state, n_paths=10_000, seed=42)
    recs = build_recommendations(state, sim)
    assert len(recs) >= 4
    for rec in recs:
        assert rec["rule"].startswith("Rule:")
        assert rec["verdict"] and rec["detail"]
