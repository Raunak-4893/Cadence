import streamlit as st

import database as db
from pages._ui import (BASE_CSS, GROTESK, INK, MUTED, SERIF, SIDEBAR_CSS,
                       active_nav_css, logo_home_button)

CSS = f"""
<style>
{BASE_CSS}
{SIDEBAR_CSS}
{active_nav_css("nav_settings")}
[data-testid="stMainBlockContainer"] {{
    max-width: 900px !important; padding: 40px 40px 48px 40px !important; }}
[data-testid="stMain"] h1 {{
    font-family: {SERIF} !important; font-weight: 600 !important; font-size: 30px !important;
    color: {INK} !important; }}
[data-testid="stMain"] h3 {{
    font-family: {SERIF} !important; font-weight: 600 !important; font-size: 20px !important;
    color: {INK} !important; }}
[data-testid="stMain"] p, [data-testid="stMain"] label p {{
    font-family: {GROTESK} !important; }}
[data-testid="stMain"] [data-testid="stTextInputRootElement"] {{
    height: 47px !important; min-height: 47px !important; border-radius: 10px !important;
    border: 1px solid #E4E4EE !important; background: #FFFFFF !important;
    box-shadow: none !important; }}
[data-testid="stMain"] .stTextInput input {{
    font-family: {GROTESK} !important; font-size: 14px !important;
    padding: 12px 14px !important; height: 45px !important; }}
[data-testid="stMain"] .stButton > button {{
    height: 44px !important; min-height: 44px !important; border-radius: 8px !important;
    background: #5A5AAB !important; border: 1px solid #5A5AAB !important;
    box-shadow: none !important; }}
[data-testid="stMain"] .stButton > button p {{
    font-family: {GROTESK} !important; font-weight: 600 !important;
    font-size: 15px !important; color: #FFFFFF !important; }}
[data-testid="stMain"] [data-testid="stVerticalBlock"] {{ gap: 0.75rem !important; }}
</style>
"""


def settings():
    st.markdown(CSS, unsafe_allow_html=True)
    logo_home_button()
    user_id = st.session_state.user[0]
    user = db.get_user_by_id(user_id)

    st.title("Settings")
    st.write("Manage your account details.")

    st.divider()

    # ---- Change name ----
    st.subheader("Change name")

    current_name = user[1] if user else ""
    new_name = st.text_input("New name", value=current_name, key="sg_new_name")

    if st.button("Update name", use_container_width=True, key="sg_update_name"):
        if not new_name.strip():
            st.error("Name cannot be empty.")
        else:
            db.update_user_name(user_id, new_name)
            st.session_state.user = db.get_user_by_id(user_id)
            st.success("Name updated!")
            st.rerun()

    st.divider()

    # ---- Change password ----
    st.subheader("Change password")

    current_password = st.text_input("Current password", type="password", key="sg_current_password")
    new_password = st.text_input("New password", type="password", key="sg_new_password")
    confirm_password = st.text_input("Confirm new password", type="password", key="sg_confirm_password")

    if st.button("Update password", use_container_width=True, key="sg_update_password"):
        if not current_password or not new_password or not confirm_password:
            st.error("Please fill in all password fields.")
        elif len(new_password) < 8:
            st.error("New password must be at least 8 characters.")
        elif new_password != confirm_password:
            st.error("New passwords do not match.")
        else:
            email = user[2] if user else ""
            verified = db.verify_user(email, current_password)
            if not verified:
                st.error("Current password is incorrect.")
            else:
                db.update_user_password(user_id, new_password)
                st.success("Password updated!")