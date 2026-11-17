"""⚡ Live AI Simulation — price options with your own parameters."""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.pricing import (
    heston_price, merton_price, heston_greeks, merton_greeks,
    check_put_call_parity, binomial_american_call, MONEYNESS_GRID,
)
from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="Live Simulation — OptionLab Pro", page_icon="⚡", layout="wide")
apply_theme()
render_badge_bar()

st.title("⚡ Live AI Simulation")
st.markdown(
    '<div class="section-note">Price European, American and barrier options with the '
    '<b>Heston stochastic-volatility</b> and <b>Merton jump-diffusion</b> models using '
    'Monte Carlo simulation. Defaults reproduce the original research study.</div>',
    unsafe_allow_html=True,
)

# ------------------------------- inputs -------------------------------------
with st.sidebar:
    st.header("🎛️ Market Parameters")
    S0 = st.number_input("Initial stock price (S₀)", 1.0, 10_000.0, 80.0, step=1.0)
    K = st.number_input("Strike price (K)", 1.0, 10_000.0, 80.0, step=1.0)
    r = st.slider("Risk-free rate r (%)", 0.0, 15.0, 5.5, 0.25) / 100
    T = st.slider("Time to maturity (months)", 1, 24, 3, 1) / 12
    sigma = st.slider("Base volatility σ (%)", 1.0, 100.0, 35.0, 1.0) / 100
    n_sims = st.select_slider("Monte Carlo paths", [5_000, 10_000, 20_000, 50_000, 100_000], 20_000)
    steps = st.select_slider("Time steps", [50, 100, 250], 100)
    seed = st.number_input("Random seed", 0, 10_000, 42)

    st.divider()
    st.header("🔬 Model Parameters")
    st.caption("Heston (Team Member A)")
    rho = st.slider("Correlation ρ", -0.95, 0.0, -0.30, 0.05)
    v0 = st.number_input("Initial variance ν₀", 0.001, 1.0, 0.032, format="%.3f")
    kappa = st.number_input("Mean-reversion speed κ", 0.1, 10.0, 1.85, format="%.2f")
    theta = st.number_input("Long-run variance θ", 0.001, 1.0, 0.045, format="%.3f")
    st.caption("Merton (Team Member B)")
    lamb = st.slider("Jump intensity λ", 0.0, 3.0, 0.75, 0.05)
    mu_j = st.number_input("Jump mean µ", -2.0, 0.0, -0.5, 0.05)
    sigma_j = st.number_input("Jump volatility δ", 0.0, 1.0, 0.22, 0.01)

tab_sim, tab_payoff, tab_strikes = st.tabs(
    "🎯 Option Prices & Greeks", "📐 Payoff & Simulation", "📈 Multi-Strike Sweep"
)

# --------------------------- option pricing ---------------------------------
with tab_sim:
    colL, colR = st.columns(2)
    with colL:
        st.subheader("🌊 Heston — Stochastic Volatility")
        hp_call = heston_price(S0, K, r, T, rho, "call", v0, kappa, theta,
                               sigma, n_sims, steps, seed)
        hp_put = heston_price(S0, K, r, T, rho, "put", v0, kappa, theta,
                              sigma, n_sims, steps, seed)
        a, b = st.columns(2)
        a.metric("ATM European Call", f"${hp_call:,.2f}")
        b.metric("ATM European Put", f"${hp_put:,.2f}")
        d_c, g_c = heston_greeks(S0, K, r, T, rho, "call", h=0.5,
                                 num_paths=n_sims, num_steps=steps, seed=seed)
        d_p, g_p = heston_greeks(S0, K, r, T, rho, "put", h=0.5,
                                 num_paths=n_sims, num_steps=steps, seed=seed)
        st.dataframe(pd.DataFrame({
            "Option": ["Call", "Put"], "Delta": [round(d_c, 4), round(d_p, 4)],
            "Gamma": [round(g_c, 4), round(g_p, 4)]}), use_container_width=True)

    with colR:
        st.subheader("💥 Merton — Jump-Diffusion")
        mp_call = merton_price(S0, K, r, T, lamb, "call", sigma, mu_j, sigma_j,
                               n_sims, seed)
        mp_put = merton_price(S0, K, r, T, lamb, "put", sigma, mu_j, sigma_j,
                              n_sims, seed)
        a, b = st.columns(2)
        a.metric("European Call", f"${mp_call:,.2f}")
        b.metric("European Put", f"${mp_put:,.2f}")
        md_c, mg_c = merton_greeks(S0, K, r, T, lamb, "call", h=0.5,
                                   num_paths=n_sims, seed=seed)
        md_p, mg_p = merton_greeks(S0, K, r, T, lamb, "put", h=0.5,
                                   num_paths=n_sims, seed=seed)
        st.dataframe(pd.DataFrame({
            "Option": ["Call", "Put"], "Delta": [round(md_c, 4), round(md_p, 4)],
            "Gamma": [round(mg_c, 4), round(mg_p, 4)]}), use_container_width=True)

    st.divider()
    st.subheader("🇺🇸 American Call (CRR binomial tree) & 🚧 Barrier Options")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("American Call (tree)", f"${binomial_american_call(S0, K, r, sigma, T):,.2f}")
    c2.metric("European Call (BSM-adj.)", f"${mp_call:,.2f}")
    c3.metric("Up-and-In Call", "custom", "set B > S₀ in scenarios")
    c4.metric("Down-and-In Put", "custom", "set B < S₀ in scenarios")

    # put-call parity
    st.divider()
    st.subheader("✅ Put–Call Parity Validation (Q11)")
    rows = []
    for name, cp, pp in [("Heston", hp_call, hp_put), ("Merton", mp_call, mp_put)]:
        holds, disc, lhs, rhs = check_put_call_parity(cp, pp, S0, K, r, T)
        rows.append({"Model": name, "|C − P|": round(lhs, 4),
                     "S₀ − K·e^(−rT)": round(rhs, 4), "Gap": round(disc, 4),
                     "Holds (< 0.05)": "✅ Yes" if holds else "❌ No"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.caption("Parity holding within Monte Carlo noise confirms both engines are internally consistent.")

# --------------------------- payoff / paths ---------------------------------
with tab_payoff:
    from utils.pricing import heston_mc_paths, merton_mc_paths
    from utils.pricing import SIGMA_DEFAULT, V0_Heston, KAPPA_Heston, THETA_Heston, SIGMA_V_Heston, MU_J_Merton, SIGMA_J_Merton

    st.subheader("Simulated terminal prices & payoff profile")
    S_h, _ = heston_mc_paths(S0, v0, kappa, theta, sigma, rho, T, min(n_sims, 20_000),
                             steps, r, seed=seed)
    S_m = merton_mc_paths(S0, r, sigma, T, lamb, mu_j, sigma_j,
                          min(n_sims, 20_000), steps, seed=seed)

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=S_h[:, -1], nbinsx=80, name="Heston S_T",
                               opacity=0.62, marker_color="#6C5CE7"))
    fig.add_trace(go.Histogram(x=S_m[:, -1], nbinsx=80, name="Merton S_T",
                               opacity=0.62, marker_color="#00CEC9"))
    fig.add_vline(x=K, line_dash="dash", line_color="#e17055",
                  annotation_text=f"Strike K = ${K:.0f}")
    fig.update_layout(barmode="overlay", height=430,
                      title="Distribution of terminal stock prices (T = %.2f yr)" % T,
                      xaxis_title="Terminal stock price S_T ($)", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)

    sample = S_h[np.random.RandomState(0).choice(len(S_h), 25, replace=False)]
    fig2 = go.Figure()
    xs = np.linspace(0, T, steps + 1)
    for row in sample:
        fig2.add_trace(go.Scatter(x=xs, y=row, mode="lines", opacity=0.4,
                                  line=dict(width=1, color="#6C5CE7"), showlegend=False))
    fig2.add_hline(y=K, line_dash="dash", line_color="#e17055")
    fig2.update_layout(height=430, title="Sample Heston price paths (25 of the simulation)",
                       xaxis_title="Time (years)", yaxis_title="Stock price ($)")
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------- strike sweep -----------------------------------
with tab_strikes:
    st.subheader("Q12 — Call prices across 7 equally spaced moneyness strikes")
    from utils.pricing import strike_sweep
    df = strike_sweep(S0, r, T, rho, lamb, n_sims, steps, seed)
    st.dataframe(df, use_container_width=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Strike (K)"], y=df["Heston Call Price"],
                             mode="lines+markers", name="Heston", line=dict(color="#6C5CE7", width=3)))
    fig.add_trace(go.Scatter(x=df["Strike (K)"], y=df["Merton Call Price"],
                             mode="lines+markers", name="Merton", line=dict(color="#e17055", width=3)))
    fig.update_layout(height=430, title="Call price vs strike — Heston vs Merton",
                      xaxis_title="Strike price ($)", yaxis_title="Call price ($)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(
    """<div class="disclaimer"><b>⚠️ Educational Disclaimer</b><br>
    This application is developed for educational, research, and demonstration purposes only.
    Predictions generated by this system should not be considered financial, investment, legal,
    medical, or professional advice. Consult qualified professionals before making decisions
    based on the results provided by this platform.</div>""",
    unsafe_allow_html=True,
)
