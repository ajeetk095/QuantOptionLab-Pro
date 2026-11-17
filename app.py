"""
OptionLab Pro — Home page (Streamlit multipage entry point).

Production-quality web application converted from the research project
"Beyond Black-Scholes: Pricing Options Under Stochastic Volatility and Jumps"
(MScFE 620 — Derivative Pricing, Group Work Project #2, Group #9450).

Home page now includes a LIVE MARKET PULSE: real-time quotes (yfinance, no API
key), a Monte Carlo simulation on the live spot & realised volatility, and
transparent rule-based recommendation cards for visitors.

Developer: Ajeet Kumar — ajeetk095@gmail.com
"""

import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.theme import apply_theme, render_badge_bar
from utils.live_engine import (
    TICKER_DEFAULTS, get_market_state, run_live_simulation, build_recommendations,
)

st.set_page_config(
    page_title="OptionLab Pro — Stochastic Volatility & Jump-Diffusion Option Pricing",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_badge_bar()


# ---------------------------------------------------------------------------
# Cached live-data accessors (TTL 60 s) — the actual network calls happen only
# here, so auto-refresh never hammers the data provider.
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60, show_spinner=False)
def cached_market_state(ticker: str, days: int = 120):
    return get_market_state(ticker, days)


# ---------------------------------------------------------------------------
# Live Market Pulse — auto-refreshes every 60 s via st.fragment
# ---------------------------------------------------------------------------
@st.fragment(run_every=60)
def live_market_pulse():
    st.subheader("📡 Live Market Pulse")
    st.caption("Real-time quotes and simulation, refreshed automatically every 60 seconds. "
               "Free market data via yfinance — no API key, no secrets required.")

    csel, cnote = st.columns([1, 2])
    with csel:
        ticker = st.selectbox("Ticker", TICKER_DEFAULTS, index=0)
    with cnote:
        st.markdown('<div class="section-note">Pick any ticker above — the simulation and '
                    "recommendations below recompute on the live spot price and the realised "
                    'volatility of the last ~120 trading days.</div>', unsafe_allow_html=True)

    state = cached_market_state(ticker)

    # ---------------- graceful fallback banner ----------------
    if not state["live"]:
        st.warning(
            f"🟡 **Live data delayed / unavailable** for `{ticker}` (cloud data providers can be "
            "rate-limited). Showing **Demo Mode** with this project's research parameters — "
            "S₀ = $80, σ = 35%, r = 5.5% — so every feature stays usable. "
            f"Last attempt: {state['error_time'].strftime('%H:%M:%S UTC')}.",
            icon="⚠️",
        )

    sim = run_live_simulation(state)
    spot, sigma, K = state["spot"], state["sigma"], sim["K"]

    # ---------------- live quote row ----------------
    q = state["quote"]
    m1, m2, m3, m4, m5 = st.columns(5)
    if q:
        m1.metric(f"{ticker} spot", f"${spot:,.2f}",
                  f"{q['change_pct']:+.2f}% vs prev close", )
        m2.metric("Previous close", f"${q['previous_close']:,.2f}")
    else:
        m1.metric(f"{ticker} (demo)", f"${spot:,.2f}")
        m2.metric("Previous close", "— (demo)")
    m3.metric("Realised vol (ann.)", f"{sigma * 100:.1f}%")
    m4.metric("ATM strike used", f"${K:,.2f}")
    stamp = (q["timestamp"] if q else state["error_time"]).strftime("%H:%M:%S UTC")
    m5.metric("Last update", stamp, "auto-refresh: 60 s")

    st.caption(f"🕒 Quote timestamp: {stamp} · data source: Yahoo Finance via yfinance (delayed "
               "quotes possible) · realised volatility from daily log returns, annualised (√252).")

    # ---------------- simulation output ----------------
    p = sim["prices"]
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("European call (MC)", f"${p['european_call_mc']:,.2f}")
    s2.metric("European put (MC)", f"${p['european_put_mc']:,.2f}")
    s3.metric("Heston call (ρ=−0.30)", f"${p['heston_call']:,.2f}")
    s4.metric("Merton call (λ=0.75)", f"${p['merton_call']:,.2f}")
    s5.metric("American call (tree)", f"${p['american_call']:,.2f}")

    # terminal distribution chart
    hist_fig = go.Figure()
    hist_fig.add_trace(go.Histogram(x=sim["st_terminal"], nbinsx=70, name="S_T distribution",
                                    marker_color="#6C5CE7", opacity=0.75))
    hist_fig.add_vline(x=sim["ci_lo"], line_dash="dot", line_color="#00CEC9",
                       annotation_text=f"5th pct ${sim['ci_lo']:.0f}")
    hist_fig.add_vline(x=sim["ci_hi"], line_dash="dot", line_color="#00CEC9",
                       annotation_text=f"95th pct ${sim['ci_hi']:.0f}")
    hist_fig.add_vline(x=K, line_dash="dash", line_color="#e17055",
                       annotation_text=f"Strike ${K:.0f}")
    hist_fig.update_layout(height=330, title="Monte Carlo terminal price distribution (live inputs)",
                           xaxis_title="Terminal stock price ($)", yaxis_title="Frequency")
    st.plotly_chart(hist_fig, use_container_width=True)

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("P(−10% move by horizon)", f"{sim['prob_down_10'] * 100:.1f}%")
    sc2.metric("P(+10% move by horizon)", f"{sim['prob_up_10'] * 100:.1f}%")
    sc3.metric("Expected return over horizon", f"{sim['exp_return'] * 100:.2f}%")

    # ---------------- recommendation cards ----------------
    st.divider()
    st.subheader("💡 Live Recommendations")
    st.caption("Transparent rule-based signals derived from the live simulation — every card "
               "shows the exact rule that fired.")
    recs = build_recommendations(state, sim)
    rcols = st.columns(min(3, len(recs)))
    for i, rec in enumerate(recs):
        with rcols[i % len(rcols)]:
            st.markdown(
                f"""<div class="kpi-card" style="text-align:left; margin-bottom:.7rem">
                <div class="kpi-label" style="color:var(--primary); font-size:.8rem">{rec['title']}</div>
                <div style="font-weight:700; margin:.25rem 0">{rec['verdict']}</div>
                <div style="font-size:.75rem; color:var(--muted)">{rec['rule']}</div>
                <div style="font-size:.75rem; color:var(--muted); margin-top:.25rem">{rec['detail']}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        """<div class="disclaimer" style="margin-top:.8rem"><b>⚠️ Educational Disclaimer</b><br>
        The live data, simulations, predictions, insights and recommendations on this page are for
        <b>educational, research and demonstration purposes only</b> and are <b>not financial,
        investment, legal or professional advice</b>. Quotes may be delayed and models are
        simplified. Consult a qualified professional before making any financial decision. The
        developer assumes no responsibility for actions taken based on this platform.</div>""",
        unsafe_allow_html=True,
    )


live_market_pulse()

# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Quantitative Finance · Monte Carlo Simulation · Streamlit</div>
      <h1>📈 OptionLab&nbsp;Pro</h1>
      <div class="hero-tagline">Beyond Black-Scholes — Pricing Options Under
      <b>Stochastic Volatility</b> and <b>Jump-Diffusion</b></div>
      <p>
        OptionLab Pro converts a peer-graded master's-level research project into an
        interactive AI-powered pricing platform. It prices European, American and
        exotic (barrier) options with the <b>Heston stochastic-volatility model</b> and the
        <b>Merton jump-diffusion model</b>, using Monte Carlo simulation with antithetic-style
        variance reduction, and validates every result with put–call parity and
        numerical Greeks (Delta &amp; Gamma).
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.page_link("pages/1_Live_Simulation.py", label="🚀 Run Simulation", icon="⚡")
with c2:
    st.page_link("pages/6_Research_Report.py", label="📄 View Report", icon="📄")
with c3:
    st.page_link("pages/7_Presentation.py", label="🎞️ Presentation", icon="🎞️")
with c4:
    st.page_link("pages/8_About_Developer.py", label="👨‍💻 Connect", icon="🤝")

st.divider()

# ---------------------------------------------------------------------------
# KPI highlights — research baseline
# ---------------------------------------------------------------------------
st.subheader("🏆 Research Highlights")
st.caption(
    "Baseline headline results from the original Monte Carlo study "
    "(S₀ = $80, K = $80 ATM, r = 5.5%, σ = 35%, T = 3 months, 100,000+ simulated paths)."
)

k1, k2, k3, k4, k5, k6 = st.columns(6)

def kpi(col, value, label, sub=""):
    with col:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div>""",
            unsafe_allow_html=True,
        )

kpi(k1, "$3.46", "Heston ATM Call", "ρ = −0.30 (Q5)")
kpi(k2, "$3.49", "Heston ATM Call", "ρ = −0.70 (Q6)")
kpi(k3, "$5.10", "Merton ATM Call", "λ = 0.75 (Q8)")
kpi(k4, "$2.56", "Up-and-In Call", "B = K = $95 (Q14)")
kpi(k5, "$3.52", "Down-and-In Put", "B = K = $65 (Q15)")
kpi(k6, "≈ $0.02", "Parity Gap", "Put–call parity holds (Q11)")

with st.expander("📊 Full baseline result table (from the research report)", expanded=False):
    st.markdown(
        """
        | Question | Model / Setting | Result |
        |---|---|---|
        | Q5 | Heston ATM European Call / Put (ρ = −0.30) | $3.46 / $2.38 |
        | Q6 | Heston ATM European Call / Put (ρ = −0.70) | $3.49 / $2.39 |
        | Q8 | Merton ATM European Call / Put (λ = 0.75) | $5.10 / $9.52 |
        | Q9 | Merton ATM European Call / Put (λ = 0.25) | $5.74 / $6.52 |
        | Q11 | Put–call parity, all four cases | Holds (gap ≈ 0.01–0.02) |
        | Q14 | Up-and-In call vs vanilla call (Heston, ρ = −0.70) | $2.56 vs $4.19 (≈ 39% cheaper) |
        | Q15 | Down-and-In put vs vanilla put (Merton, λ = 0.75) | $3.52 vs $9.52 |

        *These values are computed live by the simulation engine — rerun them with
        your own parameters on the Live Simulation page.*
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Why this project matters
# ---------------------------------------------------------------------------
col_a, col_b = st.columns([2, 1])
with col_a:
    st.subheader("🌍 Why This Project Matters")
    st.markdown(
        """
        - **Real-world importance** — Real markets are not lognormal. Volatility clusters,
          spikes during sell-offs and prices jump on news. Black-Scholes' constant-volatility
          assumption materially misprices tail risk; the Heston and Merton models capture it.
        - **Industry relevance** — Stochastic-volatility and jump models are the workhorses of
          modern derivatives desks: volatility surface fitting, structured-product pricing,
          exotics desks and model-validation teams all rely on exactly these frameworks.
        - **Educational value** — The platform shows, step by step, how Monte Carlo simulation,
          finite-difference Greeks, put–call parity checks and barrier-path monitoring work —
          the same tooling used in production quantitative research.
        """
    )
with col_b:
    st.markdown(
        """<div class="info-card">
        <h4>🧭 Quick tour</h4>
        <ul>
          <li><b>Live Market Pulse</b> — live quotes, simulation &amp; recommendations (above)</li>
          <li><b>Live Simulation</b> — price options with your own parameters</li>
          <li><b>AI Explainability</b> — sensitivity, greeks &amp; scenario testing</li>
          <li><b>Real-Time Data</b> — live market history &amp; rolling volatility</li>
          <li><b>Learn</b> — how the models work, in plain language</li>
        </ul></div>""",
        unsafe_allow_html=True,
    )

st.divider()

st.markdown(
    """<div class="disclaimer">
    <b>⚠️ Educational Disclaimer</b><br>
    This application is developed for educational, research, and demonstration purposes only.
    The predictions, insights, analyses, and recommendations generated by this system should not
    be considered financial, investment, legal, medical, or professional advice. Users should
    consult qualified professionals before making decisions based on the results provided by
    this application. The developer assumes no responsibility for actions taken based on
    information produced by this platform.</div>""",
    unsafe_allow_html=True,
)
