"""👨‍💻 About Developer — professional profile, journey timeline."""

import streamlit as st
from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="About Developer — OptionLab Pro", page_icon="👨‍💻", layout="wide")
apply_theme()
render_badge_bar()
st.title("👨‍💻 About the Developer")

LINKEDIN = "https://www.linkedin.com/in/ajeek095/"
GITHUB   = "https://github.com/ajeetk095"
PHOTO    = "https://media.licdn.com/dms/image/v2/D5603AQHv97cmwfVvxQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1692917722661?e=1796256000&v=beta&t=rtYuIUh4p9Oh01mJNFIYKD-86EL0vjqA3UoFGVO640E"

c1, c2 = st.columns([1, 2])
with c1:
    st.markdown(f"""<div class="info-card" style="text-align:center">
      <img src="{PHOTO}" style="width:140px;height:140px;border-radius:50%;object-fit:cover;
           border:3px solid var(--accent);margin-bottom:.6rem">
      <h3>Ajeet Kumar</h3>
      <div class="section-note">Quantitative Finance Professional<br>Bangalore, India</div>
      </div>""", unsafe_allow_html=True)
    st.markdown(
        "[![Email](https://img.shields.io/badge/Email-ajeetk095%40gmail.com-red)]"
        "(mailto:ajeetk095@gmail.com)\n"
        f"[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2)]({LINKEDIN})\n"
        f"[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717)]({GITHUB})"
    )
with c2:
    st.markdown(
        "Hi, I'm **Ajeet Kumar** — a quantitative finance professional based in Bangalore. I hold a "
        "**B.Tech in IT** (AKTU), an **M.Tech in CSE** (NSUT Delhi, CGPA 7.92), and an **M.Sc. in "
        "Financial Engineering** from **WorldQuant University** (88%).\n\n"
        "I work at the intersection of tech and finance — **Python, C++, SQL** — applying "
        "**Markowitz MVO, Black-Litterman, Monte Carlo** and ML (**Random Forest, deep learning**) "
        "to real problems. Projects span portfolio optimization, Fama-French factor analysis and "
        "covariance denoising; internships at **Amul GCMMF** and **Algo8.ai** (AI defect detection "
        "via computer vision). **1st Place — Algo8 ML Hackathon, IIT Kanpur**; **felicitated by the "
        "President of India** for academic excellence.\n\n"
        "Now seeking a full-time role in **quantitative research or financial engineering**."
    )

st.divider()
st.subheader("🛠️ Skills")

skills = {
    "Languages": [
        ("Python", "python", "3776AB"),
        ("C++", "cplusplus", "00599C"),
        ("SQL", "mysql", "4479A1"),
    ],
    "Libraries & Frameworks": [
        ("NumPy", "numpy", "013243"),
        ("pandas", "pandas", "150458"),
        ("scikit-learn", "scikitlearn", "F7931E"),
        ("SciPy", "scipy", "8CAAE6"),
        ("CVXPY", "python", "3776AB"),
        ("statsmodels", "python", "3776AB"),
        ("OpenCV", "opencv", "5C3EE8"),
        ("FastAPI", "fastapi", "009688"),
    ],
    "Quant & Portfolio Methods": [
        ("Markowitz MVO", "chartdotjs", "FF6384"),
        ("Black-Litterman", "chartdotjs", "FF6384"),
        ("Kelly Criterion", "chartdotjs", "FF6384"),
        ("Fama-French 5-Factor", "chartdotjs", "FF6384"),
        ("Ledoit-Wolf", "chartdotjs", "FF6384"),
        ("CVaR", "chartdotjs", "FF6384"),
        ("Monte Carlo", "chartdotjs", "FF6384"),
    ],
    "Machine Learning": [
        ("Random Forest", "scikitlearn", "F7931E"),
        ("PCA", "scikitlearn", "F7931E"),
        ("Reinforcement Learning", "openaigym", "0081A5"),
        ("Supervised Classification", "scikitlearn", "F7931E"),
    ],
    "Generative AI & LLMs": [
        ("LLMs", "openai", "412991"),
        ("Prompt Engineering", "openai", "412991"),
        ("RAG", "langchain", "1C3C3C"),
        ("LangChain", "langchain", "1C3C3C"),
        ("FAISS", "meta", "0467DF"),
        ("Chroma", "databricks", "FF3621"),
        ("HF Transformers", "huggingface", "FFD21E"),
        ("LoRA / Fine-Tuning", "huggingface", "FFD21E"),
    ],
    "Tools & Platforms": [
        ("MySQL", "mysql", "4479A1"),
        ("Excel", "microsoftexcel", "217346"),
        ("Tableau", "tableau", "E97627"),
        ("Git", "git", "F05032"),
        ("Windows", "windows", "0078D6"),
        ("Linux", "linux", "FCC624"),
    ],
}

for category, items in skills.items():
    st.markdown(f"**{category}**")
    cols = st.columns(4)
    for i, (name, slug, color) in enumerate(items):
        cols[i % 4].markdown(
            f'<img src="https://img.shields.io/badge/{name.replace(" ", "%20")}-{color}'
            f'?style=for-the-badge&logo={slug}&logoColor=white" alt="{name}">',
            unsafe_allow_html=True,
        )
    st.markdown("<div style='margin-bottom:.8rem'></div>", unsafe_allow_html=True)

st.divider()
st.subheader("🧭 Developer Journey")
journey = [
    ("💡 Idea Generation", "Constant-volatility models misprice tail risk — proved it with real simulation."),
    ("📚 Research", "Heston (1993), Merton (1976), volatility surfaces (Gatheral 2006), jumps (Cont & Tankov 2004)."),
    ("🧮 Model Development", "Heston Euler MC, Merton compound-Poisson, FD Greeks, binomial American pricer, barriers."),
    ("🧪 Testing", "Put–call parity (gaps ≈ $0.02), reproducible seeds, benchmarks across 7 strikes."),
    ("🚀 Deployment", "Research notebook → production Streamlit: live simulation, explainability, education."),
    ("🔮 Future Vision", "Live calibration, LSM American pricing under stochastic vol, deep hedging with RL."),
]
for title, body in journey:
    st.markdown(f"""<div class="info-card" style="margin-bottom:.6rem"><b>{title}</b><br>
    <span style="color:var(--muted)">{body}</span></div>""", unsafe_allow_html=True)
