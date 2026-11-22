"""👨‍💻 About Developer & Contact — profile and quick-connect form."""

import logging
import re
import smtplib
from email.message import EmailMessage

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

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        subject = st.text_input("Subject")
        message = st.text_area("Message", height=180)
        submitted = st.form_submit_button("Send Message", use_container_width=True)

    if submitted:
        errors = []
        if len(name.strip()) < 2:
            errors.append("Please enter your name (min. 2 characters).")
        if "\r" in name or "\n" in name:
            errors.append("Name cannot contain line breaks.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""):
            errors.append("Please enter a valid email address.")
        if len(subject.strip()) < 3:
            errors.append("Subject must be at least 3 characters.")
        if "\r" in subject or "\n" in subject:
            errors.append("Subject cannot contain line breaks.")
        if len(message.strip()) < 10:
            errors.append("Message must be at least 10 characters.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                email_settings = st.secrets.get("email", {})
                smtp_host = email_settings.get("smtp_host", "smtp.gmail.com")
                smtp_port = int(email_settings.get("smtp_port", 465))
                smtp_username = email_settings.get("username", "")
                smtp_password = email_settings.get("password", "")
                to_address = email_settings.get("to_address", "ajeetk095@gmail.com")

                if not smtp_username or not smtp_password:
                    raise RuntimeError("Contact email credentials are not configured.")

                mail = EmailMessage()
                mail["From"] = smtp_username
                mail["To"] = to_address
                mail["Reply-To"] = email.strip()
                mail["Subject"] = subject.strip()
                mail.set_content(
                    f"New contact form message\n\n"
                    f"Name: {name.strip()}\n"
                    f"Email: {email.strip()}\n"
                    f"Subject: {subject.strip()}\n\n"
                    f"Message:\n{message.strip()}"
                )

                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as smtp:
                    smtp.login(smtp_username, smtp_password)
                    smtp.send_message(mail)

                st.success("✅ Your message was sent successfully. Thank you!")
            except Exception:
                logging.exception("Failed to send contact form email")
                st.error(
                    "We couldn't send your message right now. Please try again later or email "
                    "ajeetk095@gmail.com directly."
                )

    st.markdown(
        """<div class="section-note">Typical response time: within 24–48 hours. Please include the
        role or collaboration context in your message.</div>""",
        unsafe_allow_html=True,
    )
