"""📚 Documentation — installation, structure, usage, deployment, FAQ, troubleshooting."""

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="Documentation — OptionLab Pro", page_icon="📚", layout="wide")
apply_theme()
render_badge_bar()
st.title("📚 Documentation")

tab1, tab2, tab3, tab4 = st.tabs("🚀 Installation & Usage", "📁 Project Structure", "☁️ Deployment", "❓ FAQ & Troubleshooting")

with tab1:
    st.markdown("### Installation")
    st.code(
        "git clone <your-repo-url>\n"
        "cd optionlab-pro\n"
        "python -m venv .venv && source .venv/bin/activate   # Windows: .venv\\Scripts\\activate\n"
        "pip install -r requirements.txt\n"
        "streamlit run app.py",
        language="bash",
    )
    st.markdown("### Requirements\n"
                "Python 3.10+, pip packages pinned in `requirements.txt` "
                "(streamlit, numpy, pandas, plotly, altair, matplotlib, pytest).")
    st.markdown("### Usage")
    st.markdown(
        "- **Home** — overview and headline research results.\n"
        "- **Live Simulation** — set market & model parameters in the sidebar and price options instantly.\n"
        "- **AI Explainability** — tornado sensitivity, Greeks profiles, correlation impact, what-if scenarios.\n"
        "- **Real-Time Data** — live prices & rolling volatility from free APIs (demo fallback built in).\n"
        "- **Learn / Report / Presentation / Assistant / Contact / Docs** — education and resources.\n\n"
        "Model details: Heston Euler scheme with reflected variance; Merton compound-Poisson jumps; "
        "central finite-difference Greeks; CRR binomial American call; path max/min barrier monitoring. "
        "No external API keys are required anywhere in the app."
    )

with tab2:
    st.code(
        """optionlab-pro/
├── app.py                    # Home page (entry point)
├── pages/
│   ├── 1_Live_Simulation.py  # ⚡ Pricing engine UI
│   ├── 2_AI_Explainability.py# 🔍 Sensitivity & scenario testing
│   ├── 3_Real_Time_Data.py   # 📡 Live market data + demo fallback
│   ├── 4_Learn.py            # 🎓 Educational section
│   ├── 5_AI_Assistant.py     # 🤖 Rule-based Q&A assistant
│   ├── 6_Research_Report.py  # 📄 Embedded report + downloads
│   ├── 7_Presentation.py     # 🎞️ 15-slide deck viewer
│   ├── 8_About_Developer.py  # 👨‍💻 Profile & journey
│   ├── 9_Contact.py          # ✉️ Validated contact form
│   └── 10_Documentation.py   # 📚 This page
├── utils/
│   ├── pricing.py            # Core quant engine (Heston/Merton/Greeks/barriers)
│   ├── theme.py              # Shared CSS & KPI helpers
│   └── market_data.py        # Free-API data fetch with demo fallback
├── reports/                  # Original research report PDF
├── ppt/                      # Generated presentation (PPTX + PDF)
├── documentation/            # deployment.md, architecture notes
├── tests/                    # pytest suite for the pricing engine
├── streamlit_config/         # .streamlit config theme
├── requirements.txt · runtime.txt · Dockerfile · Procfile
├── README.md · LICENSE · .gitignore · deployment.md""",
        language="text",
    )

with tab3:
    st.markdown("Full step-by-step guides (GitHub, Streamlit Cloud, Hugging Face Spaces, Railway, "
                "Render, Docker) live in **[deployment.md](deployment.md)** and on the "
                "deployment page of the README. Quick start with Docker:")
    st.code("docker build -t optionlab-pro .\ndocker run -p 8501:8501 optionlab-pro", language="bash")

with tab4:
    st.markdown("### FAQs")
    st.markdown(
        "- **Do I need API keys?** No — market data uses free, key-less endpoints with a demo fallback.\n"
        "- **Why do prices differ slightly between runs?** Monte Carlo randomness; increase paths or fix the seed.\n"
        "- **Which model should I trust more?** Neither globally — Heston captures vol-of-vol/skew, "
        "Merton captures crash risk. Compare both (that's the point of the app).\n"
    )
    st.markdown("### Troubleshooting")
    st.markdown(
        "- **Port already in use** → `streamlit run app.py --server.port 8502`.\n"
        "- **Live data page shows Demo Mode** → the sandbox/network blocks the API; results fall back to study parameters.\n"
        "- **Slow simulations** → reduce Monte Carlo paths in the sidebar (10,000 is usually plenty for demos).\n"
        "- **Plotly charts not rendering** → update plotly: `pip install -U plotly`."
    )
