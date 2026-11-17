"""🤖 AI Assistant — rule-based Q&A over the model (no paid API required)."""

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="AI Assistant — OptionLab Pro", page_icon="🤖", layout="wide")
apply_theme()
render_badge_bar()
st.title("🤖 Ask the Model")
st.markdown('<div class="section-note">A built-in, rule-based assistant trained on the '
            'project\u2019s research findings. Ask about prices, greeks, parity, barriers or '
            'model intuition — instant answers, no external API needed.</div>',
            unsafe_allow_html=True)

FAQS = [
    ("what does this prediction mean",
     "The app's 'prediction' is a fair option price. It is the discounted average payoff across "
     "thousands of simulated futures of the stock under the Heston (stochastic volatility) or "
     "Merton (jump-diffusion) model. E.g. an ATM Heston call of $3.46 means: given S₀=$80, "
     "r=5.5%, 3-month horizon, the model expects the option to be worth $3.46 today."),
    ("how can i improve this result",
     "Monte Carlo accuracy improves with more paths (raise to 100,000) and more time steps "
     "(100–250). The research study used 100,000+ paths; standard error shrinks with "
     "1/√(paths). Also keep the seed fixed for reproducibility."),
    ("which feature impacts the output most",
     "The tornado analysis on the Explainability page shows: for the Merton call, spot price S₀ "
     "and volatility σ dominate; among jump parameters, jump intensity λ and mean µ matter most "
     "for puts (left-tail risk). For Heston, the correlation ρ is the key skew driver."),
    ("why is the put so expensive",
     "In the Merton study, jumps are negative on average (µ = −0.5): the left tail is fat, so "
     "downside protection is valuable. Raising jump intensity λ from 0.25 to 0.75 moved the put "
     "from $6.52 to $9.52 while the call fell from $5.74 to $5.10."),
    ("what is put call parity",
     "A no-arbitrage identity for European options: C − P = S₀ − K·e^(−rT). The app checks it "
     "automatically; in the study all four cases (Q5/Q6/Q8/Q9) held with gaps of only $0.01–0.02, "
     "confirming both engines are consistent."),
    ("what is the heston model",
     "Heston (1993) makes volatility itself random and mean-reverting around long-run level θ "
     "(speed κ), correlated with the stock (ρ). Negative ρ reproduces the leverage effect and "
     "the volatility skew observed in real markets."),
    ("what is the merton model",
     "Merton (1976) adds a compound-Poisson jump process to Black-Scholes: jumps arrive with "
     "intensity λ, with size N(µ, δ²). It captures sudden crash-like moves and fat tails."),
    ("why are barrier options cheaper",
     "Barrier options only pay if a price level is touched. In the study the up-and-in call "
     "(B=K=$95) cost $2.56 vs $4.19 for the vanilla call — a 39% saving in exchange for "
     "activation risk. The down-and-in put cost $3.52 vs $9.52."),
    ("is this investment advice",
     "No. This is an educational research demonstration. See the disclaimer — consult a "
     "qualified professional before any financial decision."),
]

q = st.text_input("Ask a question about the model, results or interpretation:",
                  placeholder="e.g. What does this prediction mean?")
if q:
    ql = q.lower()
    hits = [(i, a) for (i, a) in FAQS
            if any(w in ql for w in i.split())] or FAQS
    # rank by keyword overlap
    def score(item):
        return sum(1 for w in item[0].split() if w in ql)
    hits = sorted(hits, key=score, reverse=True)[:2]
    for _, a in hits:
        st.markdown(f"""<div class="info-card" style="margin-bottom:.7rem">{a}</div>""",
                    unsafe_allow_html=True)

st.divider()
st.subheader("💡 Try these")
cols = st.columns(3)
examples = [f[0].capitalize() + "?" for f in FAQS[:6]]
for i, ex in enumerate(examples):
    with cols[i % 3]:
        st.button(ex, key=f"ex{i}")
