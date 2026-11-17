"""
pricing.py — Core quantitative engine.

Faithful refactor of the original research notebook (DPGPW2.ipynb, Group #9450,
MScFE 620 Derivative Pricing, GWP#2). The model behaviour is preserved:

  * Heston stochastic-volatility Monte Carlo (Euler discretisation, reflected variance)
  * Merton jump-diffusion Monte Carlo (compound Poisson jumps)
  * Numerical Greeks via central finite differences
  * Put-call parity validation
  * Multi-strike (moneyness) pricing sweep
  * Barrier options (European up-and-in call, European down-and-in put)
  * CRR binomial tree for the American call (Q13)

Only engineering-level improvements were made (vectorisation, seeding, float
precision); the pricing logic and parameters are unchanged.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Global research parameters (from the GWP assignment)
# ----------------------------------------------------------------------------
S0_DEFAULT = 80.0
R_DEFAULT = 0.055
SIGMA_DEFAULT = 0.35
T_DEFAULT = 0.25  # 3 months

# Heston parameters (assignment)
V0_Heston = 0.032
KAPPA_Heston = 1.85
THETA_Heston = 0.045
SIGMA_V_Heston = 0.35

# Merton parameters (assignment)
MU_J_Merton = -0.5
SIGMA_J_Merton = 0.22


# ----------------------------------------------------------------------------
# Heston model
# ----------------------------------------------------------------------------
def heston_mc_paths(
    S0: float,
    v0: float,
    kappa: float,
    theta: float,
    sigma_v: float,
    rho: float,
    T: float,
    num_paths: int,
    num_steps: int,
    r: float,
    seed: int | None = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate Heston stock and variance paths (Euler, reflected variance)."""
    rng = np.random.default_rng(seed)
    dt = T / num_steps

    half = num_paths // 2
    Z1h = rng.standard_normal((half, num_steps))
    Z2h = rng.standard_normal((half, num_steps))
    # Antithetic variates (as in the original study) to reduce variance
    Z1 = np.vstack([Z1h, -Z1h])[:num_paths]
    Z2 = np.vstack([Z2h, -Z2h])[:num_paths]
    W1 = Z1                                   # Brownian motion for the stock
    W2 = rho * Z1 + np.sqrt(1 - rho**2) * Z2  # correlated Brownian for variance

    S = np.empty((num_paths, num_steps + 1))
    v = np.empty((num_paths, num_steps + 1))
    S[:, 0] = S0
    v[:, 0] = v0

    v_prev = v[:, 0].copy()
    S_t = S[:, 0].copy()
    for t in range(1, num_steps + 1):
        v_t = np.maximum(
            v_prev + kappa * (theta - v_prev) * dt
            + sigma_v * np.sqrt(v_prev * dt) * W2[:, t - 1],
            1e-6,
        )
        # Log-Euler update uses the PREVIOUS step's variance (as in the original
        # notebook) — this keeps E[S_t] = S0*e^{rt} exactly per step, so
        # put-call parity holds within pure sampling noise.
        S_t = S_t * np.exp((r - 0.5 * v_prev) * dt + np.sqrt(v_prev * dt) * W1[:, t - 1])
        v_prev = v_t
        v[:, t] = v_t
        S[:, t] = S_t

    return S, v


def heston_option_price(
    S_paths: np.ndarray, K: float, r: float, T: float, option_type: str = "call"
) -> float:
    """Discounted Monte Carlo payoff from simulated Heston paths."""
    ST = S_paths[:, -1]
    if option_type == "call":
        payoffs = np.maximum(ST - K, 0.0)
    elif option_type == "put":
        payoffs = np.maximum(K - ST, 0.0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")
    return float(np.exp(-r * T) * np.mean(payoffs))


def heston_price(
    S0: float,
    K: float,
    r: float,
    T: float,
    rho: float,
    option_type: str = "call",
    v0: float = V0_Heston,
    kappa: float = KAPPA_Heston,
    theta: float = THETA_Heston,
    sigma_v: float = SIGMA_V_Heston,
    num_paths: int = 20_000,
    num_steps: int = 100,
    seed: int | None = 42,
) -> float:
    S, _ = heston_mc_paths(S0, v0, kappa, theta, sigma_v, rho, T,
                           num_paths, num_steps, r, seed=seed)
    return heston_option_price(S, K, r, T, option_type)


# ----------------------------------------------------------------------------
# Merton jump-diffusion model
# ----------------------------------------------------------------------------
def merton_jump_mc(
    S0: float,
    K: float,
    r: float,
    sigma: float,
    T: float,
    lamb: float,
    mu_j: float,
    sigma_j: float,
    option_type: str = "call",
    num_paths: int = 20_000,
    seed: int | None = 42,
) -> float:
    """Merton jump-diffusion terminal-price Monte Carlo (original logic)."""
    rng = np.random.default_rng(seed)

    half = num_paths // 2
    Zh = rng.normal(0.0, 1.0, half)
    Z = np.concatenate([Zh, -Zh])[:num_paths]  # antithetic variates

    N_jumps = rng.poisson(lamb * T, num_paths)
    max_j = max(int(N_jumps.max()), 1)
    jump_log_returns = rng.normal(loc=mu_j, scale=sigma_j, size=(num_paths, max_j))
    J = np.array([
        jump_log_returns[i, :N_jumps[i]].sum() if N_jumps[i] > 0 else 0.0
        for i in range(num_paths)
    ])

    Z = rng.normal(0.0, 1.0, num_paths)
    drift = (r - lamb * (np.exp(mu_j + 0.5 * sigma_j**2) - 1) - 0.5 * sigma**2) * T
    S_T = S0 * np.exp(drift + sigma * np.sqrt(T) * Z + J)

    if option_type == "call":
        payoffs = np.maximum(S_T - K, 0.0)
    elif option_type == "put":
        payoffs = np.maximum(K - S_T, 0.0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")
    return float(np.exp(-r * T) * np.mean(payoffs))


def merton_mc_paths(
    S0: float,
    r: float,
    sigma: float,
    T: float,
    lamb: float,
    mu_j: float,
    sigma_j: float,
    num_paths: int,
    num_steps: int,
    seed: int | None = 42,
) -> np.ndarray:
    """Multi-step Merton paths (used for barrier monitoring)."""
    rng = np.random.default_rng(seed)
    dt = T / num_steps
    S_paths = np.empty((num_paths, num_steps + 1))
    S_paths[:, 0] = S0

    Z_stock = rng.normal(size=(num_paths, num_steps))
    N_jumps_per_step = rng.poisson(lamb * dt, size=(num_paths, num_steps))
    max_j = max(int(N_jumps_per_step.max()), 1)
    jump_lr = rng.normal(loc=mu_j, scale=sigma_j, size=(num_paths, num_steps, max_j))

    drift = (r - lamb * (np.exp(mu_j + 0.5 * sigma_j**2) - 1) - 0.5 * sigma**2) * dt
    for t in range(num_steps):
        step_jumps = np.array([
            jump_lr[i, t, :N_jumps_per_step[i, t]].sum() if N_jumps_per_step[i, t] > 0 else 0.0
            for i in range(num_paths)
        ])
        S_paths[:, t + 1] = S_paths[:, t] * np.exp(
            drift + sigma * np.sqrt(dt) * Z_stock[:, t] + step_jumps
        )
    return S_paths


def merton_price(
    S0: float,
    K: float,
    r: float,
    T: float,
    lamb: float,
    option_type: str = "call",
    sigma: float = SIGMA_DEFAULT,
    mu_j: float = MU_J_Merton,
    sigma_j: float = SIGMA_J_Merton,
    num_paths: int = 20_000,
    seed: int | None = 42,
) -> float:
    return merton_jump_mc(S0, K, r, sigma, T, lamb, mu_j, sigma_j,
                          option_type, num_paths, seed=seed)


# ----------------------------------------------------------------------------
# Greeks (central finite differences)
# ----------------------------------------------------------------------------
def calculate_greeks_numerical(pricing_func, S0: float, K: float, r: float, T: float,
                               h: float = 0.5, **kwargs) -> tuple[float, float]:
    """
    Delta and Gamma via central finite differences, reusing the SAME seed for
    all three perturbed prices (common random numbers) — this is an engineering
    improvement that reduces Monte Carlo noise without changing the model.
    """
    seed = kwargs.pop("seed", 42)
    price_minus = pricing_func(S0=S0 - h, K=K, r=r, T=T, seed=seed, **kwargs)
    price_0 = pricing_func(S0=S0, K=K, r=r, T=T, seed=seed, **kwargs)
    price_plus = pricing_func(S0=S0 + h, K=K, r=r, T=T, seed=seed, **kwargs)

    delta = (price_plus - price_minus) / (2 * h)
    gamma = (price_plus - 2 * price_0 + price_minus) / (h**2)
    return delta, gamma


def heston_greeks(S0, K, r, T, rho, option_type="call", h=0.5,
                  num_paths=20_000, num_steps=100, seed=42):
    kwargs = dict(rho=rho, option_type=option_type, num_paths=num_paths,
                  num_steps=num_steps, seed=seed)
    return calculate_greeks_numerical(heston_price, S0, K, r, T, h=h, **kwargs)


def merton_greeks(S0, K, r, T, lamb, option_type="call", h=0.5,
                  num_paths=20_000, seed=42):
    kwargs = dict(lamb=lamb, option_type=option_type, num_paths=num_paths, seed=seed)
    return calculate_greeks_numerical(merton_price, S0, K, r, T, h=h, **kwargs)


# ----------------------------------------------------------------------------
# Put-call parity (Q11)
# ----------------------------------------------------------------------------
def check_put_call_parity(call_price, put_price, S0, K, r, T, tolerance=0.05):
    lhs = call_price - put_price
    rhs = S0 - K * np.exp(-r * T)
    discrepancy = abs(lhs - rhs)
    return bool(discrepancy < tolerance), float(discrepancy), float(lhs), float(rhs)


# ----------------------------------------------------------------------------
# Barrier options (Q14, Q15)
# ----------------------------------------------------------------------------
def heston_up_and_in_call(S0, K, B, r, T, rho, num_paths=20_000, num_steps=100,
                          seed=42, v0=V0_Heston, kappa=KAPPA_Heston,
                          theta=THETA_Heston, sigma_v=SIGMA_V_Heston):
    """European up-and-in call under Heston (Q6 parameters for the research run)."""
    S, _ = heston_mc_paths(S0, v0, kappa, theta, sigma_v, rho, T,
                           num_paths, num_steps, r, seed=seed)
    barrier_hit = S.max(axis=1) >= B
    vanilla = np.maximum(S[:, -1] - K, 0.0)
    cui = np.where(barrier_hit, vanilla, 0.0)
    return (float(np.exp(-r * T) * np.mean(vanilla)),
            float(np.exp(-r * T) * np.mean(cui)))


def merton_down_and_in_put(S0, K, B, r, T, lamb, sigma=SIGMA_DEFAULT,
                           mu_j=MU_J_Merton, sigma_j=SIGMA_J_Merton,
                           num_paths=20_000, num_steps=100, seed=42):
    """European down-and-in put under Merton (Q8 parameters for the research run)."""
    S = merton_mc_paths(S0, r, sigma, T, lamb, mu_j, sigma_j,
                        num_paths, num_steps, seed=seed)
    barrier_hit = S.min(axis=1) <= B
    vanilla = np.maximum(K - S[:, -1], 0.0)
    pdi = np.where(barrier_hit, vanilla, 0.0)
    return (float(np.exp(-r * T) * np.mean(vanilla)),
            float(np.exp(-r * T) * np.mean(pdi)))


# ----------------------------------------------------------------------------
# American call via CRR binomial tree (Q13)
# ----------------------------------------------------------------------------
def binomial_american_call(S0, K, r, sigma, T, steps=100):
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    j = np.arange(steps + 1)
    ST = S0 * u ** (steps - j) * d ** j
    value = np.maximum(ST - K, 0.0)

    for i in range(steps - 1, -1, -1):
        value = disc * (p * value[:-1] + (1 - p) * value[1:])
        S_nodes = S0 * u ** (i - np.arange(i + 1)) * d ** np.arange(i + 1)
        value = np.maximum(value, S_nodes - K)  # early-exercise check
    return float(value[0])


# ----------------------------------------------------------------------------
# Multi-strike sweep (Q12)
# ----------------------------------------------------------------------------
MONEYNESS_GRID = [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15]


def strike_sweep(S0, r, T, rho, lamb, num_paths=20_000, num_steps=100, seed=42):
    """Price European calls across 7 equally spaced moneyness strikes (Heston vs Merton)."""
    strikes = [round(S0 / m, 2) for m in MONEYNESS_GRID]
    S_h, _ = heston_mc_paths(S0, V0_Heston, KAPPA_Heston, THETA_Heston,
                             SIGMA_V_Heston, rho, T, num_paths, num_steps, r, seed=seed)
    S_m = merton_mc_paths(S0, r, SIGMA_DEFAULT, T, lamb, MU_J_Merton,
                          SIGMA_J_Merton, num_paths, num_steps, seed=seed)
    rows = []
    for K in strikes:
        hp = heston_option_price(S_h, K, r, T, "call")
        mp = heston_option_price(S_m, K, r, T, "call")
        rows.append({
            "Moneyness (S0/K)": round(S0 / K, 4),
            "Strike (K)": K,
            "Heston Call Price": round(hp, 2),
            "Merton Call Price": round(mp, 2),
        })
    return pd.DataFrame(rows)


def full_price_table(S0=80.0, r=R_DEFAULT, T=T_DEFAULT,
                     num_paths=100_000, num_steps=200, seed=42):
    """Reproduce the headline research results Q5–Q15 in one call."""
    out = {}

    # Q5 / Q6 — Heston ATM European
    for rho, tag in [(-0.30, "Q5"), (-0.70, "Q6")]:
        S, _ = heston_mc_paths(S0, V0_Heston, KAPPA_Heston, THETA_Heston,
                               SIGMA_V_Heston, rho, T, num_paths, num_steps, r, seed=seed)
        out[f"{tag}_call"] = heston_option_price(S, S0, r, T, "call")
        out[f"{tag}_put"] = heston_option_price(S, S0, r, T, "put")

    # Q7 — Heston Greeks
    for rho, tag in [(-0.30, "Q5"), (-0.70, "Q6")]:
        for ot in ("call", "put"):
            d, g = heston_greeks(S0, S0, r, T, rho, ot, num_paths=num_paths,
                                 num_steps=num_steps, seed=seed)
            out[f"{tag}_{ot}_delta"] = d
            out[f"{tag}_{ot}_gamma"] = g

    # Q8 / Q9 — Merton ATM European
    for lamb, tag in [(0.75, "Q8"), (0.25, "Q9")]:
        out[f"{tag}_call"] = merton_jump_mc(S0, S0, r, SIGMA_DEFAULT, T, lamb,
                                            MU_J_Merton, SIGMA_J_Merton, "call",
                                            num_paths, seed=seed)
        out[f"{tag}_put"] = merton_jump_mc(S0, S0, r, SIGMA_DEFAULT, T, lamb,
                                           MU_J_Merton, SIGMA_J_Merton, "put",
                                           num_paths, seed=seed)
        for ot in ("call", "put"):
            d, g = merton_greeks(S0, S0, r, T, lamb, ot, num_paths=num_paths, seed=seed)
            out[f"{tag}_{ot}_delta"] = d
            out[f"{tag}_{ot}_gamma"] = g

    # Q11 — put-call parity
    for tag in ("Q5", "Q6", "Q8", "Q9"):
        holds, disc, lhs, rhs = check_put_call_parity(out[f"{tag}_call"],
                                                      out[f"{tag}_put"], S0, S0, r, T)
        out[f"{tag}_parity_holds"] = holds
        out[f"{tag}_parity_gap"] = disc

    # Q13 — American call (Heston context): for a non-dividend-paying stock,
    # early exercise of a call is never optimal, so the American price equals
    # the European Heston price (the report's finding: $3.48 ≈ $3.49).
    out["Q13_american_call"] = out["Q5_call"]
    out["Q13_american_call_binomial_bsm"] = binomial_american_call(S0, S0, r, SIGMA_DEFAULT, T)

    # Q14 / Q15 — barrier options
    out["Q14_vanilla"], out["Q14_cui"] = heston_up_and_in_call(
        S0, 95.0, 95.0, r, T, -0.70, num_paths, num_steps, seed)
    out["Q15_vanilla"], out["Q15_pdi"] = merton_down_and_in_put(
        S0, 65.0, 65.0, r, T, 0.75, num_paths=num_paths, num_steps=num_steps, seed=seed)

    return out
