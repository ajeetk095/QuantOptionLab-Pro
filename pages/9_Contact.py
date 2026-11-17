"""✉️ Contact Developer — validated form + quick connect buttons."""

import re

import streamlit as st

from utils.theme import apply_theme, render_badge_bar

st.set_page_config(page_title="Contact — OptionLab Pro", page_icon="✉️", layout="wide")
apply_theme()
render_badge_bar()
st.title("✉️ Contact the Developer")

b1, b2, b3 = st.columns(3)
b1.link_button("📧 Email", "mailto:ajeetk095@gmail.com", use_container_width=True)
b2.link_button("💼 LinkedIn", "https://www.linkedin.com/", use_container_width=True)  # TODO: add profile URL
b3.link_button("🐙 GitHub", "https://github.com/", use_container_width=True)  # TODO: add profile URL

st.divider()

with st.form("contact_form", clear_on_submit=True):
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message", height=140)
    submitted = st.form_submit_button("Send Message", use_container_width=True)

if submitted:
    errors = []
    if len(name.strip()) < 2:
        errors.append("Please enter your name (min. 2 characters).")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""):
        errors.append("Please enter a valid email address.")
    if len(message.strip()) < 10:
        errors.append("Message must be at least 10 characters.")
    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success(
            f"✅ Thanks, {name}! Your message was validated locally.\n\n"
            "This demo does not send email directly — please also reach me at "
            "**ajeetk095@gmail.com** and I'll get back to you promptly."
        )

st.markdown(
    """<div class="section-note">Typical response time: within 24–48 hours. For quantitative
    research collaborations, internships, or full-time roles, please mention the context in
    your message.</div>""", unsafe_allow_html=True,
)
