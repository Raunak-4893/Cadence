"""Cadence — dashboard.

1:1 implementation of the `Dashboard` section of Study_Planner.fig
(frames `Empty dashboard` and `Filled dashboard`).
"""

import html
from datetime import date, datetime

import streamlit as st

import database as db
from pages._tasks import (add_task_dialog, ensure_schedule, init_tasks,
                          weighted_progress)
from pages._ui import (BASE_CSS, GROTESK, PRIMARY, SANS, SERIF, SIDEBAR_CSS,
                       active_nav_css, logo_home_button)

# dashboard-specific tokens, taken straight from the frames
SLATE = "#364153"
GREY = "#99A1AF"
GREY_SOFT = "#8888A4"
NAV_OFF = "#6B6B85"
CARD_BD = "rgba(173,173,255,0.24)"
CARD_SH = "2px 2px 12px 0 rgba(34,34,63,0.02)"
ROW_BD = "rgba(243,244,246,0.71)"
TRACK = "#F3F4F6"
BOX_BD = "#D1D5DC"

PRIORITY = {
    "High": ("#FF6467", "#FB2C36", "Important"),
    "Important": ("#FF6467", "#FB2C36", "Important"),
    "Medium": ("#FE9A00", "#FE9A00", "Medium"),
    "Low": ("#05DF72", "#00A63E", "Low"),
}

NAV = [("dashboard", "Dashboard"), ("timetable", "My calendar"), ("settings", "All tasks")]

CSS = f"""
<style>
{BASE_CSS}

{SIDEBAR_CSS}
{active_nav_css("nav_dashboard")}
[data-testid="stMainBlockContainer"] {{
    max-width: none !important;
    padding: 32px 32px 24px 32px !important;
    box-sizing: border-box !important;
}}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
    max-width: 1126px !important; }}

/* ---------------- greeting ---------------- */
.cad-head .eyebrow {{
    font-family: {GROTESK}; font-weight: 600; font-size: 12px; line-height: 16px;
    color: {GREY_SOFT}; margin: 0; }}
.cad-head h1 {{
    font-family: {SERIF}; font-weight: 600; font-size: 30px; line-height: 37.5px;
    color: {SLATE}; margin: 0; }}
.cad-head .sub {{
    font-family: {GROTESK}; font-weight: 400; font-size: 14px; line-height: 20px;
    color: {GREY_SOFT}; margin: 0; }}
.st-key-cadadd {{
    position: absolute !important; right: 40px; top: 34px; width: auto !important; z-index: 8; }}
[data-testid="stMain"] .st-key-cadadd button {{
    width: auto !important; height: 40px !important; min-height: 40px !important;
    border-radius: 8px !important; background: {PRIMARY} !important;
    border: 1px solid {PRIMARY} !important; padding: 0 16px !important;
    justify-content: center !important; box-shadow: none !important; }}
[data-testid="stMain"] .st-key-cadadd button p {{
    font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 16px !important; line-height: 20px !important; color: #FFFFFF !important; }}

/* ---------------- stat cards ---------------- */
.cad-stats {{ display: flex; gap: 16px; margin-top: 32px; }}
.cad-stat {{
    flex: 1 1 0; height: 116px; box-sizing: border-box; padding: 20px;
    background: #FFFFFF; border: 1px solid {CARD_BD}; border-radius: 14px;
    box-shadow: {CARD_SH}; }}
.cad-stat b {{
    display: block; font-family: {GROTESK}; font-weight: 300; font-size: 30px;
    line-height: 36px; color: {PRIMARY}; }}
.cad-stat u {{
    display: block; text-decoration: none; padding-top: 4px;
    font-family: {GROTESK}; font-weight: 600; font-size: 12px; line-height: 16px;
    color: {SLATE}; }}
.cad-stat i {{
    display: block; font-style: normal; padding-top: 2px;
    font-family: {GROTESK}; font-weight: 400; font-size: 12px; line-height: 16px;
    color: {GREY}; }}

/* ---------------- panels ---------------- */
[class*="st-key-cadcard_"] {{
    background: #FFFFFF; border: 1px solid {CARD_BD}; border-radius: 16px;
    box-shadow: {CARD_SH}; padding: 16px 24px 24px 24px !important;
    box-sizing: border-box !important; margin-top: 16px !important; }}
.st-key-cadcard_today {{ min-height: 516px !important; }}
.st-key-cadcard_over {{ min-height: 305px !important; }}
.st-key-cadcard_week {{ min-height: 195px !important; }}
.hd {{
    display: flex; justify-content: space-between; align-items: center; height: 32px; }}
.hd .t {{
    font-family: {GROTESK}; font-weight: 600; font-size: 16px; line-height: 24px;
    color: {SLATE}; }}
.hd .c {{
    font-family: {GROTESK}; font-weight: 600; font-size: 16px; line-height: 16px;
    color: {GREY}; margin-left: 16px; }}
.hd .d {{
    font-family: {GROTESK}; font-weight: 500; font-size: 13px; line-height: 16px;
    color: {GREY}; white-space: nowrap; }}
.cad-prog {{ padding-top: 20px; }}
.cad-prog .r {{ display: flex; justify-content: space-between; align-items: center; height: 16px; }}
.cad-prog .r span {{
    font-family: {GROTESK}; font-weight: 400; font-size: 12px; line-height: 16px; color: {GREY}; }}
.cad-prog .r b {{
    font-family: 'DM Sans', {SANS}; font-weight: 600; font-size: 12px; line-height: 16px;
    color: {SLATE}; }}
.cad-prog .track {{
    margin-top: 6px; height: 6px; border-radius: 999px; background: {TRACK}; overflow: hidden; }}
.cad-prog .track i {{ display: block; height: 6px; border-radius: 999px; background: {PRIMARY}; }}
.cad-cardfoot {{ height: 16px; }}
.cad-empty {{
    padding: 40px 0; text-align: center;
    font-family: {GROTESK}; font-weight: 400; font-size: 14px; line-height: 21px;
    color: {GREY}; }}

/* task rows: a bare checkbox + an HTML row, laid out as the Figma row */
[class*="st-key-cadtask_"] {{
    flex-direction: row !important; align-items: center !important; gap: 12px !important;
    height: 56px !important; min-height: 56px !important;
    border: 1px solid {ROW_BD} !important; border-radius: 7.11px !important;
    padding: 0 16px !important; background: #FFFFFF !important; margin-top: 8px !important;
    box-sizing: border-box !important; }}
[class*="st-key-cadtask_"] > [data-testid="stElementContainer"]:first-child {{
    width: 16px !important; flex: 0 0 16px !important; }}
[class*="st-key-cadtask_"] > [data-testid="stElementContainer"]:last-child {{
    width: auto !important; flex: 1 1 auto !important; }}
[class*="st-key-cadtask_"] .stCheckbox {{ min-height: 16px !important; height: 16px !important; }}
[class*="st-key-cadtask_"] .stCheckbox label > div:not([data-testid]) {{
    width: 16px !important; height: 16px !important; min-width: 16px !important;
    border-radius: 4px !important; border: 1px solid {BOX_BD} !important;
    background: #FFFFFF !important; }}
[class*="st-key-cadtask_"] .stCheckbox label:has(input:checked) > div:not([data-testid]) {{
    background: {PRIMARY} !important; border-color: {PRIMARY} !important; }}
.cad-trow {{ display: flex; align-items: center; justify-content: space-between; width: 100%; }}
.cad-trow .n, .cad-vrow .n {{
    font-family: {GROTESK} !important; font-weight: 500 !important; font-size: 14px !important;
    line-height: 16px !important; color: {SLATE} !important; }}
.cad-trow.done .n, .cad-vrow.done .n {{
    text-decoration: line-through; color: {GREY} !important; }}

/* read-only row (Weekend Grind): same card, no checkbox, no interaction */
.cad-vrow {{
    display: flex; align-items: center; justify-content: space-between;
    height: 56px; min-height: 56px; box-sizing: border-box;
    border: 1px solid {ROW_BD}; border-radius: 7.11px;
    padding: 0 16px; background: #FFFFFF; margin-top: 8px; }}
.cad-meta {{ display: inline-flex; align-items: center; gap: 5.7px; }}
.cad-meta span {{
    font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 12px !important;
    line-height: 16px !important; color: {GREY} !important; }}
.cad-meta em {{
    font-style: normal; font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 12px !important; line-height: 16px !important; }}
.cad-meta .dot {{ width: 4px; height: 4px; border-radius: 50%; display: inline-block; }}
</style>
"""


def _greeting(has_tasks, name=""):
    hour = datetime.now().hour
    part = "Morning" if hour < 12 else ("Afternoon" if hour < 17 else "Evening")
    who = f", {html.escape(name)}" if name else ""
    sub = ("One step at a time — your plan is live." if has_tasks
           else "Here's your space. Add tasks and your plan takes shape.")
    st.markdown(
        f'<div class="cad-head">'
        f'<p class="eyebrow">Good {part}{who}</p>'
        f'<h1>One task at a time. You\'ve got this.</h1>'
        f'<p class="sub">{html.escape(sub)}</p></div>', unsafe_allow_html=True)
    with st.container(key="cadadd"):
        if st.button("＋  Add Task", key="db_add_task_top"):
            add_task_dialog()


def _stats(done, remaining, week_pct, overdue_pct):
    cards = [(str(done), "Completed Today", f"of {done + remaining} tasks"),
             (str(remaining), "Remaining", "tasks left today"),
             (f"{week_pct}%", "Week Progress", "completion rate"),
             (f"{overdue_pct}%", "OVERDUE", "expired tasks")]
    body = "".join(f'<div class="cad-stat"><b>{v}</b><u>{l}</u><i>{s}</i></div>'
                   for v, l, s in cards)
    st.markdown(f'<div class="cad-stats">{body}</div>', unsafe_allow_html=True)


def _meta_html(task):
    dot, text, label = PRIORITY.get(task.get("priority") or "Medium", PRIORITY["Medium"])
    subject = html.escape(task.get("subject") or "General")
    return (f'<span class="cad-meta">'
            f'<span>{int(task.get("duration") or 0)} mins</span>'
            f'<span class="dot" style="background:{GREY}"></span>'
            f'<span>{subject}</span>'
            f'<span class="dot" style="background:{dot}"></span>'
            f'<em style="color:{text}">{label}</em></span>')


def _task_rows(tasks, prefix, empty_text):
    if not tasks:
        st.markdown(f'<div class="cad-empty">{html.escape(empty_text)}</div>',
                    unsafe_allow_html=True)
        return
    for t in tasks:
        with st.container(key=f"cadtask_{prefix}{t['id']}"):
            new = st.checkbox("done", value=t["completed"], key=f"db_chk_{prefix}{t['id']}",
                              label_visibility="collapsed")
            cls = "cad-trow done" if t["completed"] else "cad-trow"
            st.markdown(f'<div class="{cls}"><span class="n">{html.escape(t["name"])}</span>'
                        f'{_meta_html(t)}</div>', unsafe_allow_html=True)
            if new != t["completed"]:
                t["completed"] = new
                db.update_task(t)
                ensure_schedule()
                st.rerun()


def _task_rows_readonly(tasks, empty_text):
    """Display-only rows: no checkbox, but they still cross out when the task is
    ticked off wherever it is actually owned (Today's plan / Overdue)."""
    if not tasks:
        st.markdown(f'<div class="cad-empty">{html.escape(empty_text)}</div>',
                    unsafe_allow_html=True)
        return
    rows = "".join(
        f'<div class="{"cad-vrow done" if t["completed"] else "cad-vrow"}">'
        f'<span class="n">{html.escape(t["name"])}</span>{_meta_html(t)}</div>'
        for t in tasks)
    st.markdown(rows, unsafe_allow_html=True)


def dashboard():
    st.markdown(CSS, unsafe_allow_html=True)
    logo_home_button()

    user = st.session_state.user
    tasks = init_tasks() if user else []
    ensure_schedule()
    today = date.today()

    todays = [t for t in tasks if not t.get("deadline") or t["deadline"] >= today]
    overdue = [t for t in tasks
               if t.get("deadline") and t["deadline"] < today and not t["completed"]]
    done = len([t for t in todays if t["completed"]])
    remaining = len(todays) - done
    week_pct = weighted_progress(tasks)
    overdue_pct = round(len(overdue) / len(tasks) * 100) if tasks else 0

    display_name = ""
    if user:
        row = db.get_user_by_id(user[0])
        if row and len(row) > 1 and row[1]:
            display_name = str(row[1]).split()[0]
    _greeting(bool(tasks), display_name)
    _stats(done, remaining, week_pct, overdue_pct)

    left, right = st.columns([714, 396], gap="small")

    with left:
        pct = weighted_progress(todays)
        with st.container(key="cadcard_today"):
            # `today` is already computed for the filtering above — just show it.
            # (%-d is Linux-only, so the day number is interpolated by hand.)
            today_label = f"{today:%A}, {today.day} {today:%B %Y}"
            st.markdown(
                f'<div class="hd"><div><span class="t">Today\'s plan</span>'
                f'<span class="c">{len(todays)} tasks</span></div>'
                f'<span class="d">{today_label}</span></div>'
                f'<div class="cad-prog"><div class="r"><span>Daily Progress</span>'
                f'<b>{pct}%</b></div>'
                f'<div class="track"><i style="width:{pct}%"></i></div></div>',
                unsafe_allow_html=True)
            _task_rows(todays, "t", "Nothing scheduled yet — add a task to get started.")

    with right:
        with st.container(key="cadcard_over"):
            st.markdown('<div class="hd"><span class="t">Overdue tasks</span></div>',
                        unsafe_allow_html=True)
            _task_rows(overdue, "o", "Nothing overdue. Nice.")

        # Read-only mirror of the weekend tasks: ticking them off happens in
        # Today's plan, and the strikethrough follows here.
        weekend = [t for t in tasks if t.get("is_weekend")]
        with st.container(key="cadcard_week"):
            st.markdown('<div class="hd"><span class="t">Weekend Grind !</span></div>',
                        unsafe_allow_html=True)
            _task_rows_readonly(weekend, "No weekend tasks queued.")
