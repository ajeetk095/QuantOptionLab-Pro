"""🎓 Educational Learning Section — how the models work, in plain language."""

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="Learn — OptionLab Pro", page_icon="🎓", layout="wide")
apply_theme()
render_badge_bar()
st.title("🎓 Learn How This Model Works")
st.caption("No prior quant background needed — every concept is explained from zero.")

st.markdown("### The story in one paragraph")
st.markdown(
    "The famous Black-Scholes model assumes markets move *smoothly* and volatility is "
    "*constant*. Real markets are rougher: volatility itself rises and falls (it **clusters**), "
    "and prices occasionally **jump** on news. This project replaces Black-Scholes with two "
    "upgrades — the **Heston model** (volatility becomes a random, mean-reverting process) and "
    "the **Merton model** (random shocks are added on top of smooth motion) — and prices "
    "options by simulating thousands of possible futures with **Monte Carlo simulation**."
)

tab1, tab2, tab3, tab4 = st.tabs("🧩 Key Ideas", "🔁 Workflow", "🧮 Model Architecture", "❓ FAQ")

with tab1:
    st.markdown(
        """
        #### 1. Monte Carlo simulation 🎲
        Roll the dice thousands of times: simulate where the stock price could end up in
        3 months, compute the option payoff each time, average, and discount to today.
        *Input → thousands of futures → one fair price.*

        #### 2. Heston's stochastic volatility 🌊
        Volatility is no longer a fixed number — it wanders around a long-run level **θ**
        (mean reversion, speed **κ**), starting at today's value **ν₀**. The correlation **ρ**
        links price falls to volatility spikes (the *leverage effect*), which is why puts
        command a premium — the volatility skew.

        #### 3. Merton's jumps 💥
        On top of smooth motion, the price can occasionally *jump*: jumps arrive randomly
        (a Poisson process with intensity **λ**) and are usually negative here (mean µ = −0.5),
        i.e. crash-like. More/fewer jumps = fatter/thinner left tail = pricier/cheaper puts.

        #### 4. Greeks (Delta & Gamma) 📐
        Delta = how much the option price moves per $1 move in the stock (your hedge ratio).
        Gamma = how much Delta itself changes (curvature). Both are estimated by nudging the
        spot price up/down and re-pricing — *finite differences*.

        #### 5. Put–call parity ✅
        A free-lunch check: `C − P = S₀ − K·e^(−rT)` must hold for European options no matter
        the model. If our simulated prices satisfy it, the engines are internally consistent.
        """
    )

with tab2:
    st.markdown("### Step-by-step workflow")
    steps = [
        ("📥 Input", "User sets S₀, K, r, σ, T and model parameters (ρ, ν₀, κ, θ or λ, µ, δ) in the sidebar."),
        ("⚙️ Processing", "The engine simulates 10,000–100,000 paths of the stock (and of variance for Heston) using Euler discretisation with correlated Brownian motions."),
        ("🎯 Prediction", "Terminal prices → payoffs → average → discount at e^(−rT) = fair option price."),
        ("📐 Sensitivities", "Finite-difference nudges of S₀ give Delta and Gamma; barriers are flagged by monitoring each path's max/min."),
        ("🧪 Validation", "Put–call parity is checked automatically; deviations ≈ $0.02 confirm correctness within Monte Carlo noise."),
        ("💡 Explanation", "Charts + plain-language interpretation are rendered so every number can be understood, not just trusted."),
    ]
    for title, body in steps:
        st.markdown(f"""<div class="info-card" style="margin-bottom:.6rem">
        <b>{title}</b><br><span style="color:var(--muted)">{body}</span></div>""",
                    unsafe_allow_html=True)

with tab3:
    st.code(
        """
Stock price (Heston)      dS = r·S dt + √v · S dW₁
Variance process (Heston) dv = κ(θ − v) dt + σᵥ√v dW₂ ,  corr(W₁,W₂) = ρ
Merton jump-diffusion     dS = r·S dt + σ·S dW + S·(Jumps)   Jumps ~ Poisson(λ)·N(µ, δ²)
Price (Monte Carlo)       V  = e^(−rT) · E[payoff(S_T)]
Delta (finite difference) Δ  = [V(S+h) − V(S−h)] / 2h
Gamma (finite difference) Γ  = [V(S+h) − 2V(S) + V(S−h)] / h²
        """,
        language="mathematica",
    )
    st.markdown(
        "**Interpretation guide** — read the app's outputs like this: a **call delta ≈ +0.53** "
        "means the call gains ≈ $0.53 per $1 rise in the stock; **put–call parity gap of $0.02** "
        "means engines agree with theory within noise; an **up-and-in call at 39% of the vanilla "
        "price** means you save premium by accepting activation risk."
    )

with tab4:
    faqs = [
        ("Why not just use Black-Scholes?",
         "Black-Scholes prices are systematically wrong for options far from the money because "
         "real volatility is neither constant nor smooth. Heston/Merton correct the tails, which "
         "is where most of the risk (and premium) lives."),
        ("Why does the put get more expensive with more negative ρ?",
         "Negative ρ means falling prices come with volatility spikes, fattening the left tail of "
         "the return distribution — exactly where puts pay off."),
        ("Why is the American call ≈ the European call here?",
         "For a non-dividend-paying stock, early exercise of a call is never optimal, so both "
         "prices coincide — the app demonstrates this numerically (Q13)."),
        ("Why are barrier options cheaper?",
         "They only activate if the price touches a barrier. Some paths never trigger them, so "
         "their expected payoff (and premium) is lower — in the study, the up-and-in call costs "
         "39% less than the vanilla call."),
        ("What does 'Monte Carlo noise' mean for me?",
         "Each run uses random draws; rerunning with more paths (or a different seed) moves prices "
         "by a few cents. That is why results are quoted to the nearest cent with 100k+ paths."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.write(a)
