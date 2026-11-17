"""📡 Real-Time Data page — live market context from free APIs (with demo fallback)."""

import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.theme import apply_theme, render_badge_bar
from utils.market_data import fetch_daily_history, fetch_spot_price, DATA_SOURCE_NOTE

st.set_page_config(page_title="Real-Time Data — OptionLab Pro", page_icon="📡", layout="wide")
apply_theme()
render_badge_bar()
st.title("📡 Real-Time Market Data")
st.markdown(
    '<div class="section-note">Free, no-key public APIs (Yahoo Finance via <code>stooq</code>/'
    '<code>yfinance</code>-free endpoints) feed the pricing engine with a live underlying price '
    'and historical volatility. Includes connectivity handling, caching and auto-refresh. '
    'If APIs are unreachable (e.g. sandboxed network), the page transparently falls back to '
    '<b>Demo Mode</b> with the research study\u2019s parameters (S₀ = $80, σ = 35%).</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("Ticker", "AAPL", help="Any public equity, e.g. AAPL, MSFT, NVDA, ^GSPC")
with c2:
    history_days = st.slider("History (days)", 30, 365, 120, 30)
with c3:
    auto = st.checkbox("Auto-refresh every 60 s", value=False)

if auto:
    st_autorefresh = getattr(st, "autorefresh", None)
    if st_autorefresh:
        st_autorefresh(interval=60_000)

@st.cache_data(ttl=300, show_spinner=True)
def cached_history(ticker: str, days: int):
    return fetch_daily_history(ticker, days)

@st.cache_data(ttl=60, show_spinner=True)
def cached_spot(ticker: str):
    return fetch_spot_price(ticker)

demo_mode = False
try:
    hist = cached_history(ticker, history_days)
    if hist is None or hist.empty:
        raise RuntimeError("empty history")
    demo_mode = False
except Exception:
    demo_mode = True
    # Deterministic demo data based on the research study parameters
    rng = np.random.default_rng(42)
    dates = pd.bdate_range(end=dt.date.today(), periods=history_days)
    rets = rng.normal(0.0003, 0.35 / np.sqrt(252), history_days)
    px = 80 * np.exp(np.cumsum(rets))
    hist = pd.DataFrame({"date": dates, "close": px}).set_index("date")

st.markdown(f"**Mode:** {'🟡 Demo Mode (API unreachable — using study parameters)' if demo_mode else '🟢 Live data'}")

spot = None
if not demo_mode:
    try:
        spot = cached_spot(ticker)
    except Exception:
        spot = float(hist["close"].iloc[-1])
else:
    spot = float(hist["close"].iloc[-1])

ret = hist["close"].pct_change().dropna()
ann_vol = float(ret.std() * np.sqrt(252))
ann_ret = float(ret.mean() * 252)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Latest price", f"${spot:,.2f}")
k2.metric("Annualised volatility", f"{ann_vol * 100:.1f}%", "σ input for pricing")
k3.metric("Annualised mean return", f"{ann_ret * 100:.1f}%")
k4.metric("Last update", dt.datetime.now().strftime("%H:%M:%S"))

fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["close"], name=f"{ticker} close",
                         line=dict(color="#6C5CE7", width=2)))
fig.update_layout(height=420, title=f"{ticker} — closing price history ({history_days} trading days)",
                  xaxis_title="Date", yaxis_title="Price ($)")
st.plotly_chart(fig, use_container_width=True)

# volatility cone / rolling vol
fig2 = go.Figure()
for w, color in [(21, "#00CEC9"), (63, "#6C5CE7")]:
    rv = hist["close"].pct_change().rolling(w).std() * np.sqrt(252)
    fig2.add_trace(go.Scatter(x=hist.index, y=rv, name=f"{w}-day rolling vol",
                              line=dict(color=color, width=2)))
fig2.add_hline(y=ann_vol, line_dash="dash", annotation_text="Full-sample vol")
fig2.update_layout(height=380, title="Rolling annualised volatility (stochastic-volatility evidence)",
                   xaxis_title="Date", yaxis_title="Annualised σ")
st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **Why this matters for the models:** the rolling-volatility chart shows volatility is NOT "
    "constant — it clusters and drifts, which is precisely what the Heston model captures. "
    "Occasional large daily moves (jumps) justify the Merton model. Plug the live σ above into "
    "the Live Simulation page to price options on today's conditions."
)

st.markdown(f'<div class="section-note">{DATA_SOURCE_NOTE}</div>', unsafe_allow_html=True)
