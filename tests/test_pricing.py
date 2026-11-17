"""tests/test_pricing.py — smoke tests for the quantitative engine."""

import numpy as np
import pytest

from utils.pricing import (
    binomial_american_call, check_put_call_parity, heston_price,
    merton_price, merton_greeks, heston_greeks, strike_sweep,
)


def test_merton_parity_holds():
    """Put-call parity must hold for European options under Merton."""
    S0 = K = 80.0
    c = merton_price(S0, K, 0.055, 0.25, 0.75, "call", num_paths=30_000, seed=42)
    p = merton_price(S0, K, 0.055, 0.25, 0.75, "put", num_paths=30_000, seed=42)
    holds, disc, _, _ = check_put_call_parity(c, p, S0, K, 0.055, 0.25)
    assert holds and disc < 0.10


def test_merton_put_more_expensive_with_more_jumps():
    p_hi = merton_price(80, 80, 0.055, 0.25, 0.75, "put", num_paths=30_000, seed=42)
    p_lo = merton_price(80, 80, 0.055, 0.25, 0.25, "put", num_paths=30_000, seed=42)
    assert p_hi > p_lo  # research finding: λ=0.75 put ($9.52) > λ=0.25 put ($6.52)


def test_heston_call_positive_and_finite():
    c = heston_price(80, 80, 0.055, 0.25, -0.30, "call", num_paths=10_000, seed=42)
    assert np.isfinite(c) and c > 0


def test_call_delta_between_0_and_1():
    d, _ = merton_greeks(80, 80, 0.055, 0.25, 0.75, "call", h=0.5,
                         num_paths=20_000, seed=42)
    assert 0.0 < d < 1.0


def test_american_call_no_early_exercise_premium():
    """Non-dividend American call ≈ European (BSM value ≈ $6.09 at σ=35%, ATM)."""
    price = binomial_american_call(80, 80, 0.055, 0.35, 0.25, steps=200)
    assert 5.5 < price < 6.8


def test_strike_sweep_shape():
    df = strike_sweep(80, 0.055, 0.25, -0.30, 0.75, num_paths=5_000, seed=42)
    assert len(df) == 7
    # strikes are listed descending (moneyness ascending) → prices increase down the table
    assert df["Heston Call Price"].is_monotonic_increasing
