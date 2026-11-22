"""👨‍💻 About Developer & Contact — profile and quick-connect form."""

import re

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

st.set_page_config(
    page_title="About & Contact — OptionLab Pro",
    page_icon="👨‍💻",
    layout="wide",
)
apply_theme()
render_badge_bar()
st.title("👨‍💻 About & Contact")

LINKEDIN = "https://www.linkedin.com/in/ajeek095/"
GITHUB = "https://github.com/ajeetk095"
PHOTO = "https://media.licdn.com/dms/image/v2/D5603AQHv97cmwfVvxQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1692917722661?e=1796256000&v=beta&t=rtYuIUh4p9Oh01mJNFIYKD-86EL0vjqA3UoFGVO640E"

profile_col, contact_col = st.columns([1, 1], gap="large")

with profile_col:
    st.subheader("About the Developer")
    st.markdown(f"""<div class="info-card" style="text-align:center">
      <img src="{PHOTO}" style="width:140px;height:140px;border-radius:50%;object-fit:cover;
           border:3px solid var(--accent);margin-bottom:.6rem">
      <h3>Ajeet Kumar</h3>
      <div class="section-note">Quantitative Finance Professional<br>Bangalore, India</div>
      </div>""", unsafe_allow_html=True)

    st.markdown(
        "Hi, I'm **Ajeet Kumar** — a quantitative finance professional based in Bangalore. I hold a "
        "**B.Tech in IT** (AKTU), an **M.Tech in CSE** (NSUT Delhi, CGPA 7.92), and an **M.Sc. in "
        "Financial Engineering** from **WorldQuant University** (88%).\n\n"
        "I work at the intersection of technology and finance, applying quantitative methods and "
        "machine learning to real-world problems. Projects span portfolio optimization, "
        "Fama-French factor analysis and covariance denoising, with experience in quantitative "
        "research and computer vision.\n\n"
        "I am seeking a full-time role in **quantitative research or financial engineering**."
    )

    b1, b2, b3 = st.columns(3)
    b1.link_button("📧 Email", "mailto:ajeetk095@gmail.com", use_container_width=True)
    b2.link_button("💼 LinkedIn", LINKEDIN, use_container_width=True)
    b3.link_button("🐙 GitHub", GITHUB, use_container_width=True)

with contact_col:
    st.subheader("Contact")
    st.caption("Send a message about opportunities, research collaborations or feedback.")

    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        subject = st.text_input("Subject")
        message = st.text_area("Message", height=180)
        submitted = st.form_submit_button("Send Message", use_container_width=True)

    if submitted:
        errors = []
        if len(name.strip()) < 2:
            errors.append("Please enter your name (min. 2 characters).")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""):
            errors.append("Please enter a valid email address.")
        if len(subject.strip()) < 3:
            errors.append("Subject must be at least 3 characters.")
        if len(message.strip()) < 10:
            errors.append("Message must be at least 10 characters.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success(
                f"✅ Thanks, {name}! Your message was validated locally.\n\n"
                "This demo does not send email directly — please also reach me at "
                "**ajeetk095@gmail.com**."
            )

    st.markdown(
        """<div class="section-note">Typical response time: within 24–48 hours. Please include the
        role or collaboration context in your message.</div>""",
        unsafe_allow_html=True,
    )
