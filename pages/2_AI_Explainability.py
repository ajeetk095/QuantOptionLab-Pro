"""🔍 AI Explainability Dashboard — sensitivity, greeks, scenario testing."""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.pricing import (
    heston_price, merton_price, heston_greeks, merton_greeks,
    V0_Heston, KAPPA_Heston, THETA_Heston, SIGMA_V_Heston,
    MU_J_Merton, SIGMA_J_Merton,
)
from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="AI Explainability — OptionLab Pro", page_icon="🔍", layout="wide")
apply_theme()
render_badge_bar()
st.title("🔍 AI Explainability Dashboard")
st.markdown('<div class="section-note">Understand <i>why</i> the models produce their prices: '
            'one-factor sensitivity analysis, Greeks across spot, correlation impact and '
            'interactive what-if scenario testing.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🎛️ Base Scenario")
    S0 = st.number_input("Spot S₀", 1.0, 5_000.0, 80.0, 1.0, key="x_S0")
    K = st.number_input("Strike K", 1.0, 5_000.0, 80.0, 1.0, key="x_K")
    r = st.slider("r (%)", 0.0, 15.0, 5.5, 0.25) / 100
    T = st.slider("T (months)", 1, 24, 3, 1) / 12
    sigma = st.slider("σ (%)", 1.0, 100.0, 35.0, 1.0) / 100
    rho = st.slider("Heston ρ", -0.95, 0.0, -0.30, 0.05)
    lamb = st.slider("Merton λ", 0.0, 3.0, 0.75, 0.05)
    n_sims = 10_000
    seed = 42

tab1, tab2, tab3, tab4 = st.tabs(
    "🎯 Parameter Sensitivity", "Γ Greeks vs Spot", "🔗 Correlation Impact", "🧪 What-If Scenarios"
)

# --------------------------- tornado sensitivity ----------------------------
with tab1:
    st.subheader("One-factor sensitivity (tornado analysis)")
    st.caption("Each factor is flexed ±25% around the base case; bars show the change in the "
               "Merton call price (a proxy for model output importance — the quantitative "
               "counterpart of feature importance in ML).")

    base_call = merton_price(S0, K, r, T, lamb, "call", sigma, MU_J_Merton,
                             SIGMA_J_Merton, n_sims, seed)
    base_put = merton_price(S0, K, r, T, lamb, "put", sigma, MU_J_Merton,
                            SIGMA_J_Merton, n_sims, seed)

    factors = {
        "Spot S₀": (S0, lambda v: merton_price(v, K, r, T, lamb, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)),
        "Strike K": (K, lambda v: merton_price(S0, v, r, T, lamb, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)),
        "Volatility σ": (sigma, lambda v: merton_price(S0, K, r, T, lamb, "call", v, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)),
        "Jump intensity λ": (lamb, lambda v: merton_price(S0, K, r, T, v, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)),
        "Jump mean µ": (MU_J_Merton, lambda v: merton_price(S0, K, r, T, lamb, "call", sigma, v, SIGMA_J_Merton, n_sims, seed)),
        "Jump vol δ": (SIGMA_J_Merton, lambda v: merton_price(S0, K, r, T, lamb, "call", sigma, MU_J_Merton, v, n_sims, seed)),
        "Rate r": (r, lambda v: merton_price(S0, K, v, T, lamb, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)),
        "Maturity T": (T, lambda v: merton_price(S0, K, r, v, lamb, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)),
    }

    rows = []
    for name, (base, fn) in factors.items():
        if base == 0:
            continue
        lo, hi = base * 0.75, base * 1.25
        p_lo, p_hi = fn(lo), fn(hi)
        rows.append({"Factor": name, "Low impact": p_lo - base_call,
                     "High impact": p_hi - base_call,
                     "Total swing": abs(p_hi - p_lo)})
    imp = pd.DataFrame(rows).sort_values("Total swing")

    fig = go.Figure()
    fig.add_trace(go.Bar(y=imp["Factor"], x=imp["Low impact"], orientation="h",
                         name="Factor −25%", marker_color="#00CEC9"))
    fig.add_trace(go.Bar(y=imp["Factor"], x=imp["High impact"], orientation="h",
                         name="Factor +25%", marker_color="#6C5CE7"))
    fig.update_layout(barmode="overlay", height=420,
                      title="Impact on Merton call price ($ change vs base case)",
                      xaxis_title="Δ price ($)", yaxis_title="Input factor")
    st.plotly_chart(fig, use_container_width=True)
    best = imp.iloc[-1]
    st.info(f"💡 **Most influential factor:** **{best['Factor']}** (total swing "
            f"${best['Total swing']:.2f}). This is the input the model 'relies on' most — "
            "analogous to the top feature in an ML feature-importance ranking.")

# --------------------------- greeks vs spot ---------------------------------
with tab2:
    st.subheader("Delta & Gamma across spot prices (numerical Greeks)")
    spots = np.linspace(S0 * 0.7, S0 * 1.3, 13)
    rows_h, rows_m = [], []
    for s in spots:
        dc, gc = heston_greeks(s, K, r, T, rho, "call", h=0.5,
                               num_paths=n_sims, num_steps=100, seed=seed)
        mc_, gm = merton_greeks(s, K, r, T, lamb, "call", h=0.5,
                                num_paths=n_sims, seed=seed)
        rows_h.append({"S": s, "Delta": dc, "Gamma": gc})
        rows_m.append({"S": s, "Delta": mc_, "Gamma": gm})
    dh, dm = pd.DataFrame(rows_h), pd.DataFrame(rows_m)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dh["S"], y=dh["Delta"], name="Heston Delta",
                             line=dict(color="#6C5CE7", width=3)))
    fig.add_trace(go.Scatter(x=dh["S"], y=dh["Gamma"], name="Heston Gamma",
                             line=dict(color="#00CEC9", width=3), yaxis="y2"))
    fig.add_trace(go.Scatter(x=dm["S"], y=dm["Delta"], name="Merton Delta",
                             line=dict(color="#e17055", width=3, dash="dot")))
    fig.update_layout(height=430, title="Greeks profile of the European call",
                      xaxis_title="Spot price ($)",
                      yaxis=dict(title="Delta"),
                      yaxis2=dict(title="Gamma", overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="section-note">Delta rises toward 1 as the call moves in-the-money; '
                'gamma peaks near the ATM point where curvature is largest — exactly where '
                'hedging is hardest.</div>', unsafe_allow_html=True)

# --------------------------- correlation impact ------------------------------
with tab3:
    st.subheader("Heston correlation ρ impact (leverage effect)")
    rhos = np.round(np.linspace(-0.90, -0.10, 9), 2)
    calls, puts = [], []
    for rr in rhos:
        calls.append(heston_price(S0, K, r, T, rr, "call", n_paths=n_sims, seed=seed))
        puts.append(heston_price(S0, K, r, T, rr, "put", n_paths=n_sims, seed=seed))
    df_rho = pd.DataFrame({"ρ": rhos, "Call price ($)": calls, "Put price ($)": puts})
    st.dataframe(df_rho.round(2), use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_rho["ρ"], y=df_rho["Call price ($)"], name="Call",
                             line=dict(color="#6C5CE7", width=3), mode="lines+markers"))
    fig.add_trace(go.Scatter(x=df_rho["ρ"], y=df_rho["Put price ($)"], name="Put",
                             line=dict(color="#e17055", width=3), mode="lines+markers"))
    fig.update_layout(height=420, title="ATM option prices vs spot–volatility correlation",
                      xaxis_title="Correlation ρ", yaxis_title="Option price ($)")
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 A more negative ρ (stronger leverage effect: price falls → volatility spikes) "
            "raises put values and left-tail risk — the stochastic-volatility explanation of "
            "the volatility skew.")

# --------------------------- what-if scenarios -------------------------------
with tab4:
    st.subheader("What-if scenario testing")
    st.caption("Compare your base case against stressed market conditions in one click.")
    scenarios = st.multiselect(
        "Pick scenarios to price (Merton call, base vs stressed):",
        ["Bear market (λ × 2)", "Vol spike (σ × 1.5)",
         "Crash jumps (µ −1.0)", "Calm market (λ × 0.3, σ × 0.7)"],
        default=["Bear market (λ × 2)", "Vol spike (σ × 1.5)"])
    base = merton_price(S0, K, r, T, lamb, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)
    st.metric("Base Merton call", f"${base:,.2f}")
    table = []
    for s in scenarios:
        if s.startswith("Bear"):
            v = merton_price(S0, K, r, T, lamb * 2, "call", sigma, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)
        elif s.startswith("Vol"):
            v = merton_price(S0, K, r, T, lamb, "call", sigma * 1.5, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)
        elif s.startswith("Crash"):
            v = merton_price(S0, K, r, T, lamb, "call", sigma, -1.0, SIGMA_J_Merton, n_sims, seed)
        else:
            v = merton_price(S0, K, r, T, lamb * 0.3, "call", sigma * 0.7, MU_J_Merton, SIGMA_J_Merton, n_sims, seed)
        table.append({"Scenario": s, "Call price ($)": round(v, 2),
                      "Δ vs base ($)": round(v - base, 2)})
    if table:
        st.dataframe(pd.DataFrame(table), use_container_width=True)
        st.markdown('<div class="section-note">Recommendation logic mirrors the research report: '
                    'in high-jump or high-volatility states, downside protection (puts) becomes '
                    'expensive quickly — hedge before stress arrives, not after.</div>',
                    unsafe_allow_html=True)
