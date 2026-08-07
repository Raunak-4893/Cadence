import streamlit as st

import database as db
from pages._tasks import COMMITMENT_HOURS, auto_schedule, daily_capacity_minutes
from pages._ui import (BASE_CSS, GROTESK, INK, MUTED, PRIMARY, RESPONSIVE_CSS,
                       SERIF, SIDEBAR_CSS, active_nav_css, logo_home_button)

# Same list, same hours-per-week figures as step 2 of onboarding.
COMMITMENTS = [("gym", "Gym", 5), ("coaching", "Coaching Classes", 8),
               ("sports", "Sports Practice", 5), ("commute", "Commute", 7),
               ("part_time", "Part-Time Job", 20),
               ("family", "Family Responsibilities", 5),
               ("extracurricular", "Extracurriculars", 5)]

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

/* ---------------- weekly routine ---------------- */
.cad-bar {{ padding-top: 10px; }}
.cad-bar .row {{ display: flex; justify-content: space-between; align-items: center; }}
.cad-bar .row span {{
    font-family: {GROTESK}; font-weight: 500; font-size: 13px; color: {MUTED}; }}
.cad-bar .row b {{
    font-family: {GROTESK}; font-weight: 700; font-size: 13px; color: {INK}; }}
.cad-bar .track {{
    margin-top: 5px; height: 6px; border-radius: 999px; background: #EFEFF6;
    overflow: hidden; }}
.cad-bar .track i {{ display: block; height: 6px; border-radius: 999px; }}
.cad-free {{
    margin-top: 14px; padding: 14px 16px; border-radius: 12px;
    background: #F4F4FC; border: 1px solid #E2E2F2; }}
.cad-free b {{
    display: block; font-family: {GROTESK}; font-weight: 700; font-size: 22px;
    line-height: 28px; color: {PRIMARY}; }}
.cad-free span {{
    font-family: {GROTESK}; font-weight: 400; font-size: 13px; color: {MUTED}; }}
{RESPONSIVE_CSS}
</style>
"""


def _routine():
    return st.session_state.onboarding.setdefault("routine", {})


def _week_totals(routine):
    """The onboarding maths, unchanged: what a week is spent on."""
    sleep = routine.get("sleep_hours", 8) * 7
    school = routine.get("school_hours", 6) * routine.get("school_days", 5)
    commitments = sum(hrs for key, _label, hrs in COMMITMENTS if routine.get(key))
    free = max(0, 168 - sleep - school - commitments)
    return sleep, school, commitments, free


def _bar(label, hours, colour):
    pct = min(100, round(hours / 168 * 100))
    return (f'<div class="cad-bar"><div class="row"><span>{label}</span>'
            f'<b>{hours}h</b></div><div class="track">'
            f'<i style="width:{pct}%;background:{colour}"></i></div></div>')


def _weekly_routine_section():
    """Step 2 of onboarding, re-opened so the answers can be changed later."""
    routine = _routine()

    st.subheader("Your weekly routine")
    st.write("The same questions from setup. Change them any time — your "
             "timetable is rebuilt from these numbers.")

    sleep_hours = st.slider("Hours of sleep a night", 4, 12,
                            int(routine.get("sleep_hours", 8)), key="sg_sleep")

    col_h, col_d = st.columns(2)
    with col_h:
        school_hours = st.number_input("Hours at school/college a day", 0, 12,
                                       int(routine.get("school_hours", 6)),
                                       key="sg_school_hours")
    with col_d:
        school_days = st.number_input("Days a week you attend", 0, 7,
                                      int(routine.get("school_days", 5)),
                                      key="sg_school_days")

    st.write("What else regularly takes up your time?")
    labels = {label: key for key, label, _ in COMMITMENTS}
    chosen = st.pills(
        "Commitments", options=list(labels),
        default=[label for key, label, _ in COMMITMENTS if routine.get(key)],
        selection_mode="multi", label_visibility="collapsed", key="sg_commitments")
    chosen = chosen or []

    weekend_on = st.toggle(
        "Weekend Grind Mode — let Saturday and Sunday take study sessions",
        value=bool(routine.get("weekend_enabled", True)), key="sg_weekend")

    # Live preview, using exactly the numbers that would be saved.
    preview = dict(routine)
    preview.update({"sleep_hours": sleep_hours, "school_hours": school_hours,
                    "school_days": school_days, "weekend_enabled": weekend_on})
    for key, label, _hrs in COMMITMENTS:
        preview[key] = label in chosen
    sleep, school, commitments, free = _week_totals(preview)

    st.markdown(
        _bar("Sleep", sleep, "#8880C8") + _bar("School / college", school, "#0EA5E9")
        + _bar("Other commitments", commitments, "#F97316")
        + _bar("Free time", free, "#059669")
        + f'<div class="cad-free"><b>{free / 7:.1f} hours a day</b>'
        f'<span>is what Cadence will plan your study sessions into '
        f'({free}h free across the week).</span></div>',
        unsafe_allow_html=True)

    if st.button("Save routine", use_container_width=True, key="sg_save_routine"):
        routine.update({"sleep_hours": int(sleep_hours),
                        "school_hours": int(school_hours),
                        "school_days": int(school_days),
                        "weekend_enabled": bool(weekend_on)})
        for key, label, _hrs in COMMITMENTS:
            routine[key] = label in chosen
        db.save_onboarding_profile(st.session_state.user[0],
                                   st.session_state.onboarding)
        # capacity changed, so the week has to be re-spread against it
        auto_schedule()
        # no rerun: the widgets already hold the saved values, and rerunning
        # would wipe the confirmation before it could be read
        st.success(f"Saved. Your timetable now plans "
                   f"{daily_capacity_minutes() / 60:.1f} hours of study a day.")


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

    st.divider()

    _weekly_routine_section()