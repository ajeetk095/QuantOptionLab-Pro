"""theme.py — shared theming helpers (custom CSS, light/dark support)."""

import streamlit as st

CSS = """
<style>
:root{
  --primary:#6C5CE7; --primary-dark:#4834d4; --accent:#00CEC9;
  --bg:#f7f7fb; --card:#ffffff; --text:#1e1e2f; --muted:#6b7280;
  --good:#00b894; --warn:#e17055; --border:#e5e7eb;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#0e1117; --card:#171d27; --text:#e8eaed; --muted:#9aa3af; --border:#2a3140; }
}
/* Streamlit theme-aware overrides */
[data-testid="stAppViewContainer"]{ background: var(--bg); }
.stApp header{ background: transparent; }

.hero{
  background: linear-gradient(135deg, rgba(108,92,231,.14), rgba(0,206,201,.12));
  border:1px solid var(--border); border-radius:18px; padding:2rem 2rem 1.4rem;
  margin-bottom:1rem;
}
.hero h1{ margin:.2rem 0; font-size:2.6rem; letter-spacing:-.5px;
  background:linear-gradient(90deg,var(--primary),var(--accent));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-kicker{ color:var(--primary); font-weight:700; font-size:.8rem;
  text-transform:uppercase; letter-spacing:1.5px; }
.hero-tagline{ font-size:1.15rem; color:var(--text); margin:.3rem 0 .6rem; }
.hero p{ color:var(--muted); font-size:.98rem; max-width:900px; }

.kpi-card{
  background:var(--card); border:1px solid var(--border); border-radius:14px;
  padding:.9rem .9rem .7rem; text-align:center; height:100%;
  box-shadow:0 1px 4px rgba(0,0,0,.05);
}
.kpi-value{ font-size:1.5rem; font-weight:800; color:var(--primary); }
.kpi-label{ font-size:.8rem; font-weight:600; color:var(--text); margin-top:.15rem; }
.kpi-sub{ font-size:.72rem; color:var(--muted); }

.info-card{
  background:var(--card); border:1px solid var(--border); border-radius:14px;
  padding:1rem 1.2rem; height:100%;
}
.info-card h4{ margin-top:0; color:var(--primary); }
.info-card ul{ padding-left:1.1rem; color:var(--text); }

.disclaimer{
  background:rgba(225,112,85,.10); border:1px solid rgba(225,112,85,.45);
  border-radius:14px; padding:1rem 1.2rem; color:var(--text); font-size:.9rem;
}
.section-note{ color:var(--muted); font-size:.9rem; }
.pill{
  display:inline-block; padding:.15rem .65rem; border-radius:999px;
  background:rgba(108,92,231,.12); color:var(--primary); font-weight:600; font-size:.78rem;
  margin-right:.35rem;
}
.badgebar{ display:flex; gap:.5rem; flex-wrap:wrap; margin:.2rem 0 .8rem; }
.badge{
  font-size:.72rem; padding:.2rem .6rem; border-radius:8px; font-weight:700;
  background:var(--card); border:1px solid var(--border); color:var(--muted);
}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def render_badge_bar():
    st.markdown(
        """<div class="badgebar">
        <span class="badge">🐍 Python · Streamlit</span>
        <span class="badge">🎲 Monte Carlo</span>
        <span class="badge">🌊 Heston Model</span>
        <span class="badge">💥 Merton Jump-Diffusion</span>
        <span class="badge">📊 Plotly</span>
        <span class="badge">🎓 MScFE 620 Research</span>
        </div>""",
        unsafe_allow_html=True,
    )


def kpi_card(value: str, label: str, sub: str = "") -> str:
    return (
        f"""<div class="kpi-card"><div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div>"""
    )
