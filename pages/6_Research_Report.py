"""📄 Research Report — embedded full report, summary, downloads."""

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

SUMMARY_MD = """OptionLab Pro — Research Summary

Study: Beyond Black-Scholes — Heston stochastic volatility & Merton jump-diffusion
option pricing via Monte Carlo (MScFE 620 GWP#2, Group 9450).

Key results: Heston ATM call/put $3.46/$2.38 (rho=-0.30) and $3.49/$2.39 (rho=-0.70);
Merton ATM call/put $5.10/$9.52 (lambda=0.75) and $5.74/$6.52 (lambda=0.25);
put-call parity holds in all cases (gaps ~$0.02); up-and-in call $2.56 vs $4.19
vanilla (-39%); down-and-in put $3.52 vs $9.52 vanilla."""

st.set_page_config(page_title="Research Report — OptionLab Pro", page_icon="📄", layout="wide")
apply_theme()
render_badge_bar()
st.title("📄 Research Report")
st.caption("Group Work Project #2 · Group 9450 · MScFE 620: Derivative Pricing · WorldQuant University")

col1, col2 = st.columns(2)
with col1:
    try:
        with open("reports/GPW2_9450_report-1.pdf", "rb") as f:
            st.download_button("⬇️ Download full report (PDF)", f.read(),
                               "GPW2_9450_report.pdf", "application/pdf",
                               use_container_width=True)
    except FileNotFoundError:
        st.info("Report PDF not bundled — see the project zip /reports folder.")
with col2:
    summary_md = st.session_state.get("summary_md", SUMMARY_MD)
    st.download_button("⬇️ Download summary (Markdown)", summary_md.encode("utf-8"),
                       "report_summary.md", "text/markdown", use_container_width=True)

st.subheader("Executive Summary")
st.markdown(
    "This project investigates pricing of **European, American and exotic options** with models "
    "that incorporate realistic market behaviour: **stochastic volatility** (Heston) and "
    "**jump-diffusion** (Merton). Using Monte Carlo simulation (100,000+ paths, 100–250 steps, "
    "variance reduction), the study priced ATM options under two correlation regimes and two jump "
    "intensities, computed numerical Greeks, validated put–call parity, swept 7 moneyness strikes, "
    "and priced barrier options (up-and-in call, down-and-in put)."
)

tab_results, tab_concl, tab_reco = st.tabs(["📊 Key Results", "🧾 Conclusions", "✅ Recommendations"])

with tab_results:
    st.markdown(
        """
        | Question | Model / Setting | Result |
        |---|---|---|
        | Q5 | Heston ATM Call / Put, ρ = −0.30 | $3.46 / $2.38 |
        | Q6 | Heston ATM Call / Put, ρ = −0.70 | $3.49 / $2.39 |
        | Q7 | Heston Greeks (ρ=−0.30): Δ_call/Δ_put; Γ_call/Γ_put | +0.53/−0.46; −0.03/0.04 |
        | Q8 | Merton ATM Call / Put, λ = 0.75 | $5.10 / $9.52 |
        | Q9 | Merton ATM Call / Put, λ = 0.25 | $5.74 / $6.52 |
        | Q10 | Merton Greeks (Q8 Call): Δ, Γ | 0.473, 0.0235 |
        | Q11 | Put–call parity, Q5/Q6/Q8/Q9 | Holds; gaps ≈ $0.01–0.02 |
        | Q12 | 7 strikes (moneyness 0.85–1.15) | Heston ≥ Merton, converging ATM |
        | Q13 | American call ≈ European call | No early-exercise premium (no dividends) |
        | Q14 | Up-and-in call vs vanilla (K=B=$95) | $2.56 vs $4.19 (−39%) |
        | Q15 | Down-and-in put vs vanilla (K=B=$65) | $3.52 vs $9.52 |
        """
    )

with tab_concl:
    st.markdown(
        """
        - **Leverage effect pricing:** more negative spot–volatility correlation (ρ: −0.30 → −0.70)
          raises put values and gamma — volatility spikes during declines fatten the left tail.
        - **Jump risk is asymmetric:** higher jump intensity (λ: 0.25 → 0.75) makes puts far more
          expensive (+46%) while calls get cheaper, because the jump mean (µ = −0.5) is crash-like.
        - **Model agreement & validation:** both models satisfy put–call parity within Monte Carlo
          noise; Heston prices OTM calls slightly above Merton, reflecting vol-of-vol tail risk.
        - **Barriers trade premium for activation risk:** barrier structures cost ~39% (CUI) to
          ~63% (PDI) less than vanilla equivalents.
        """
    )

with tab_reco:
    st.markdown(
        """
        - **For hedgers:** with strongly negative ρ, hedge with options (gamma) rather than
          delta-only — convexity demand rises in stressed regimes.
        - **For income/insurance buyers:** buy puts before stress regimes arrive; jump intensity
          is regime-dependent and repricing is fast.
        - **For cost-conscious exposure:** barrier structures offer large premium savings when
          activation risk is acceptable; model them with stochastic volatility, not constant vol.
        - **For model validators:** put–call parity is a cheap, powerful first-line check on any
          Monte Carlo pricing engine.
        """
    )

st.divider()
st.subheader("References (MLA)")
st.markdown(
    "- Cont, Rama, and Peter Tankov. *Financial Modelling with Jump Processes*. Chapman and Hall/CRC, 2004.\n"
    "- Gatheral, Jim. *The Volatility Surface: A Practitioner's Guide*. Wiley Finance, 2006.\n"
    "- Heston, Steven L. \"A Closed-Form Solution for Options with Stochastic Volatility…\" *The Review of Financial Studies* 6.2 (1993): 327–343.\n"
    "- Hull, John C. *Options, Futures, and Other Derivatives*. 10th ed., Pearson, 2018.\n"
    "- Merton, Robert C. \"Option Pricing When Underlying Stock Returns Are Discontinuous.\" *J. of Financial Economics* 3.1–2 (1976): 125–144.\n"
    "- Wilmott, Paul. *Paul Wilmott on Quantitative Finance*. 2nd ed., Wiley, 2006."
)
