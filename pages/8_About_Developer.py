"""👨‍💻 About Developer — professional profile, journey timeline."""

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="About Developer — OptionLab Pro", page_icon="👨‍💻", layout="wide")
apply_theme()
render_badge_bar()
st.title("👨‍💻 About the Developer")

c1, c2 = st.columns([1, 2])
with c1:
    st.markdown("""<div class="info-card" style="text-align:center">
      <div style="font-size:4rem">🧑‍💼</div>
      <h3>Ajeet Kumar</h3>
      <div class="section-note">Quantitative Finance Professional<br>Bangalore, India</div>
      </div>""", unsafe_allow_html=True)
    st.markdown(
        "[![Email](https://img.shields.io/badge/Email-ajeetk095%40gmail.com-red)]"
        "(mailto:ajeetk095@gmail.com)\n"
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2)]"
        "(https://www.linkedin.com/)  <!-- TODO: add LinkedIn URL -->\n"
        "[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717)]"
        "(https://github.com/)  <!-- TODO: add GitHub URL -->"
    )
with c2:
    st.markdown(
        "Hi, I'm **Ajeet Kumar**, a quantitative finance aspiring professional based in Bangalore, "
        "India. I hold a **B.Tech in Information Technology** from Dr. A.P.J. Abdul Kalam Technical "
        "University and an **M.Tech in Computer Science and Engineering** from Netaji Subhas "
        "University of Technology, New Delhi (CGPA 7.92). I recently graduated from **WorldQuant "
        "University** with an **M.Sc. in Financial Engineering, scoring 88%**.\n\n"
        "My work sits at the intersection of technology and finance. I'm skilled in **Python, C++ "
        "and SQL**, and I've spent the last few years applying quantitative methods — **Markowitz "
        "MVO, Black-Litterman, Monte Carlo Simulation** — alongside machine learning techniques "
        "like **Random Forest and deep learning** to real problems.\n\n"
        "I've put this into practice through projects in portfolio optimization, Fama-French factor "
        "analysis and covariance denoising, and through internships at **Amul GCMMF** and "
        "**Algo8.ai**, where I built AI-driven defect detection systems using computer vision. "
        "I won **1st Place at the Algo8 ML Hackathon at IIT Kanpur** and was **felicitated by the "
        "President of India** for academic excellence.\n\n"
        "I'm now looking to bring this mix of finance and engineering skill to a full-time role in "
        "**quantitative research or financial engineering**."
    )

st.divider()
st.subheader("🛠️ Skills")
sc = st.columns(5)
skills = [
    ("AI / ML", "🤖"), ("Data Science", "📊"), ("Computer Vision", "👁️"),
    ("Reinforcement Learning", "🎮"), ("Portfolio Optimization", "📈"),
]
for (name, icon), col in zip(skills, sc):
    col.markdown(f"""<div class="kpi-card"><div style="font-size:1.6rem">{icon}</div>
    <div class="kpi-label">{name}</div></div>""", unsafe_allow_html=True)
sc2 = st.columns(2)
for (name, icon), col in zip([("Python", "🐍"), ("SQL", "🗄️")], sc2):
    col.markdown(f"""<div class="kpi-card"><div style="font-size:1.6rem">{icon}</div>
    <div class="kpi-label">{name}</div></div>""", unsafe_allow_html=True)

st.divider()
st.subheader("🧭 Developer Journey")
journey = [
    ("💡 Idea Generation", "Noticed that constant-volatility models misprice tail risk — wanted to "
                           "demonstrate the difference with real simulation."),
    ("📚 Research", "Studied Heston (1993) and Merton (1976), volatility surfaces (Gatheral 2006) "
                    "and jump processes (Cont & Tankov 2004)."),
    ("🧮 Model Development", "Implemented Heston Euler simulation, Merton compound-Poisson MC, "
                             "finite-difference Greeks, binomial American pricer and barrier logic."),
    ("🧪 Testing", "Validated with put–call parity (gaps ≈ $0.02), reproducibility seeds and "
                   "benchmark comparisons across 7 strikes."),
    ("🚀 Deployment", "Refactored the research notebook into this production Streamlit platform — "
                      "live simulation, explainability dashboard and educational content."),
    ("🔮 Future Vision", "Parameter calibration to live markets, LSM American pricing under "
                         "stochastic volatility, deep hedging with reinforcement learning."),
]
for title, body in journey:
    st.markdown(f"""<div class="info-card" style="margin-bottom:.6rem"><b>{title}</b><br>
    <span style="color:var(--muted)">{body}</span></div>""", unsafe_allow_html=True)
