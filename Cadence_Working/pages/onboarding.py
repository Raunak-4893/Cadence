"""Cadence — onboarding wizard.

1:1 implementation of the `Onboarding` section of Study_Planner.fig
(7 frames = 3 wizard steps + the "Your plan is ready" screen).
"""

import streamlit as st

import database as db
from const import SUGGESTED_SUBJECTS
from pages._ui import (BASE_CSS, BAR_FILL, BAR_TRACK, CANVAS, CHIP_BD, CHIP_BG, FAINT,
                       GROTESK, INK, INK_SOFT, LINE, LINE_RAIL, MUTED, PRIMARY,
                       HIDE_SIDEBAR, PRIMARY_DEEP, PRIMARY_MID, RAIL, SANS, SEL_BD,
                       SEL_BG, SERIF, brand)

STEPS = ["Get to know you", "Your weekly routine", "Your subjects"]

# the "focus loop" illustration from the Figma left rail, redrawn as vectors
FOCUS_LOOP = (
    '<svg width="180" height="180" viewBox="0 0 540 540" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="270" cy="270" r="268.5" fill="none" stroke="#B4B4CC" stroke-width="3"/>'
    '<circle cx="270" cy="270" r="172.5" fill="none" stroke="#B4B4CC" stroke-width="3"/>'
    '<circle cx="270" cy="270" r="75" fill="#B1AECE"/>'
    '<circle cx="270" cy="270" r="42.5" fill="#615B9B"/></svg>')

STUDENT_TYPES = ["School Student", "College Student", "Competitive Exams", "Something else"]
GOALS = [("\U0001F4CB", "Staying on top of my tasks"), ("⏰", "Managing my time better"),
         ("\U0001F331", "Building consistent habits"), ("\U0001F3AF", "Reducing procrastination"),
         ("\U0001F4DA", "Preparing for exams"), ("\U0001F60C", "Feeling less overwhelmed")]

COMMITMENTS = [("gym", "Gym", 5), ("coaching", "Coaching Classes", 8),
               ("sports", "Sports Practice", 5), ("commute", "Commute", 7),
               ("part_time", "Part-Time Job", 20), ("family", "Family Responsibilities", 5),
               ("extracurricular", "Extracurriculars", 5)]

CSS = f"""
<style>
{BASE_CSS}
{HIDE_SIDEBAR}

/* ---------------- shell: 547px rail + content + sticky action bar ---------------- */
[data-testid="stMainBlockContainer"] {{
    margin-left: 547px !important;
    width: calc(100% - 547px) !important;
    min-height: 100vh !important;
    padding: 56px 80px 138px 80px !important;
    border-left: 1px solid {LINE_RAIL};
    box-sizing: border-box !important;
}}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
    max-width: 732px !important; }}

.cad-rail {{
    position: fixed; top: 0; left: 0; bottom: 0; width: 547px; height: 100vh;
    background: {RAIL}; padding: 40px 0 32px 56px; box-sizing: border-box;
    display: flex; flex-direction: column; z-index: 9;
}}
.cad-rail-steps {{ margin-top: 40px; display: flex; flex-direction: column; gap: 20px; }}
.cad-step {{ display: flex; align-items: center; gap: 14px; height: 26px; }}
.cad-step .n {{
    width: 26px; height: 26px; border-radius: 50%; flex: 0 0 26px;
    display: flex; align-items: center; justify-content: center;
    font-family: {SANS}; font-weight: 600; font-size: 12px; line-height: 18px;
}}
.cad-step.todo .n {{ border: 1px solid {FAINT}; color: {FAINT}; }}
.cad-step.now  .n {{ background: {PRIMARY_DEEP}; color: #FFFFFF; }}
.cad-step.done .n {{ background: {PRIMARY_MID}; color: #FFFFFF; }}
.cad-step .l {{ font-family: {GROTESK}; font-size: 14px; line-height: 21px; }}
.cad-step.todo .l {{ font-weight: 400; color: {FAINT}; }}
.cad-step.now  .l {{ font-weight: 600; color: {INK}; }}
.cad-step.done .l {{ font-weight: 400; color: {INK_SOFT}; }}

.cad-rail-art {{ padding-top: 72px; display: flex; justify-content: center; }}
.cad-rail-art svg {{ display: block; }}
.cad-rail-lede {{
    padding: 48px 56px 0 0;
    font-family: {GROTESK}; font-weight: 400; font-size: 24px; line-height: 35.1px;
    color: {INK}; margin: 0; max-width: 435px;
}}
.cad-rail-spacer {{ flex: 1 1 auto; min-height: 16px; }}
.cad-rail-foot {{
    padding-right: 56px; font-family: {GROTESK}; font-weight: 400;
    font-size: 13px; line-height: 20px; color: {FAINT}; margin: 0;
}}

/* live "Your Week" preview */
.cad-live {{ padding: 48px 40px 0 0; }}
.cad-live h4 {{
    font-family: {GROTESK}; font-weight: 500; font-size: 12px; line-height: 16.5px;
    color: {FAINT}; margin: 0; letter-spacing: .02em; }}
.cad-live .big {{ display: flex; align-items: baseline; gap: 13px; padding-top: 6px; }}
.cad-live .big b {{
    font-family: {GROTESK}; font-weight: 700; font-size: 56px; line-height: 56px;
    color: {INK}; }}
.cad-live .big span {{
    font-family: {GROTESK}; font-weight: 400; font-size: 14px; line-height: 21px;
    color: {FAINT}; }}
.cad-bars {{ padding-top: 20px; display: flex; flex-direction: column; gap: 14px; }}
.cad-bar .row {{ display: flex; justify-content: space-between; align-items: center; height: 20px; }}
.cad-bar .row span {{
    font-family: {GROTESK}; font-weight: 400; font-size: 13px; line-height: 19.5px;
    color: {INK_SOFT}; }}
.cad-bar .row b {{
    font-family: {SANS}; font-weight: 500; font-size: 13px; line-height: 19.5px;
    color: {INK_SOFT}; }}
.cad-bar .track {{
    margin-top: 5px; height: 6px; border-radius: 4px; background: {BAR_TRACK}; overflow: hidden; }}
.cad-bar .track i {{ display: block; height: 6px; border-radius: 4px; background: {BAR_FILL}; }}

/* ---------------- right column typography ---------------- */
.cad-h1 {{
    font-family: {SERIF} !important; font-weight: 400 !important; font-size: 34px !important;
    line-height: 43.52px !important; color: {INK} !important; margin: 0 !important;
    max-width: 560px; }}
.cad-lede {{
    font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 14px !important;
    line-height: 21px !important; color: {MUTED} !important; margin: 0 !important;
    padding-top: 8px !important; max-width: 540px; white-space: pre-line; }}
.cad-bubble {{
    display: inline-flex !important; align-items: center; margin-top: 32px;
    background: {RAIL}; border-radius: 18px; padding: 13px 32px;
    font-family: {GROTESK}; font-weight: 400; font-size: 14px; line-height: 20px; color: {INK}; }}
.cad-q {{
    font-family: {GROTESK} !important; font-weight: 500 !important; font-size: 14px !important;
    line-height: 21px !important; color: {INK} !important; margin: 0 !important;
    padding-top: 32px !important; }}
.cad-q.tight {{ padding-top: 20px !important; }}

/* ---------------- option cards ---------------- */
[data-testid="stMain"] .stButton > button {{
    width: 100%; border-radius: 12px; border: 1px solid #E0E0E0;
    background: #FFFFFF; color: {INK}; box-shadow: none !important;
    justify-content: flex-start; padding: 0 16px !important;
}}
[data-testid="stMain"] .stButton > button p {{
    font-family: {GROTESK} !important; font-weight: 400 !important;
    font-size: 14px !important; line-height: 21px !important; color: {INK} !important; }}
[data-testid="stMain"] .stButton > button:hover {{
    border-color: {SEL_BD}; background: #FCFCFF; color: {INK}; }}

[class*="st-key-cadopt_"] {{ padding-top: 10px !important; }}
[class*="st-key-cadopt_"] button {{ height: 50px !important; min-height: 50px !important; }}
[data-testid="stMain"] [class*="st-key-cadopt_"] button p::before {{
    content: ""; display: inline-block; width: 16px; height: 16px; margin-right: 12px;
    border: 1px solid #C0C0C0; border-radius: 50%; vertical-align: -3px; }}
[class*="st-key-cadsel_"] {{ padding-top: 10px !important; }}
[class*="st-key-cadsel_"] button {{
    height: 50px !important; min-height: 50px !important;
    background: {SEL_BG} !important; border: 1px solid {SEL_BD} !important; }}
[data-testid="stMain"] [class*="st-key-cadsel_"] button p {{ font-weight: 500 !important; }}
[data-testid="stMain"] [class*="st-key-cadsel_"] button p::before {{
    content: ""; display: inline-block; width: 16px; height: 16px; margin-right: 12px;
    border-radius: 50%; vertical-align: -3px;
    background: radial-gradient(circle, {PRIMARY_MID} 0 4px, transparent 4px); }}

/* goal cards carry their emoji in the label, so no radio dot */
[class*="st-key-cadgoal_"] {{ padding-top: 10px !important; }}
[class*="st-key-cadgoal_"] button {{
    height: 47px !important; min-height: 47px !important; border-color: {LINE} !important; }}
[class*="st-key-cadgsel_"] {{ padding-top: 10px !important; }}
[class*="st-key-cadgsel_"] button {{
    height: 47px !important; min-height: 47px !important;
    background: {SEL_BG} !important; border: 1px solid {SEL_BD} !important; }}
[data-testid="stMain"] [class*="st-key-cadgsel_"] button p {{ font-weight: 500 !important; }}

/* ---------------- pills (commitments / suggested subjects) ---------------- */
[class*="st-key-cadpill_"] button, [class*="st-key-cadpsel_"] button {{
    width: auto !important; height: 36px !important; min-height: 36px !important;
    border-radius: 20px !important; border: 1px solid {LINE_RAIL} !important;
    padding: 0 14px !important; justify-content: center !important; }}
[data-testid="stMain"] [class*="st-key-cadpill_"] button p, [data-testid="stMain"] [class*="st-key-cadpsel_"] button p {{
    font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 14px !important; line-height: 20px !important; color: {INK_SOFT} !important; }}
[class*="st-key-cadpsel_"] button {{
    background: {PRIMARY_DEEP} !important; border-color: {PRIMARY_DEEP} !important; }}
[data-testid="stMain"] [class*="st-key-cadpsel_"] button p {{ color: #FFFFFF !important; }}

/* ---------------- rows ---------------- */
[class*="st-key-cadrow_"] {{
    flex-direction: row !important; flex-wrap: wrap !important; gap: 8px !important;
    align-items: flex-start !important; padding-top: 12px !important; }}
[class*="st-key-cadrow_"] > [data-testid="stLayoutWrapper"],
[class*="st-key-cadrow_"] > [data-testid="stElementContainer"] {{ width: auto !important; }}
[class*="st-key-cadgrid_"], [class*="st-key-cadgridg_"] {{
    flex-direction: row !important; flex-wrap: wrap !important; gap: 0 10px !important;
    align-items: flex-start !important; }}
[class*="st-key-cadgrid_"] > [data-testid="stLayoutWrapper"] {{ width: 266px !important; }}
[class*="st-key-cadgridg_"] > [data-testid="stLayoutWrapper"] {{ width: 274px !important; }}

/* ---------------- slider / stepper / segmented ---------------- */
.cad-metric {{ display: flex; justify-content: space-between; align-items: center;
    padding-top: 32px; }}
.cad-metric span {{
    font-family: {GROTESK}; font-weight: 500; font-size: 14px; line-height: 21px; color: {INK}; }}
.cad-metric b {{
    font-family: {SANS}; font-weight: 500; font-size: 16px; line-height: 18px; color: {PRIMARY}; }}
[data-testid="stMain"] .stSlider {{ padding-top: 4px !important; }}
[data-testid="stMain"] .stSlider [data-testid="stWidgetLabel"] {{ display: none !important; }}
[data-testid="stMain"] .stSlider [data-baseweb="slider"] div[role="slider"] {{
    background: {BAR_FILL} !important; }}
[data-testid="stMain"] .stSlider [data-testid="stSliderTickBar"] {{
    font-family: {SANS} !important; }}
[data-testid="stMain"] .stSlider [data-testid="stSliderTickBarMin"],
[data-testid="stMain"] .stSlider [data-testid="stSliderTickBarMax"] {{
    font-family: {SANS} !important; font-size: 14px !important; color: {FAINT} !important; }}
[data-testid="stMain"] [data-testid="stSliderThumbValue"] {{ display: none !important; }}
[data-testid="stMain"] [data-testid="stSlider"] [data-orientation="horizontal"] > div:first-child {{
    height: 8px !important; border-radius: 6px !important; }}
[data-testid="stMain"] [data-testid="stSliderTickBar"] p {{
    font-family: {SANS} !important; font-weight: 400 !important; font-size: 14px !important;
    line-height: 18px !important; color: {FAINT} !important; }}

[class*="st-key-cadstep_"] {{
    flex-direction: row !important; gap: 3px !important; align-items: center !important;
    padding-top: 16px !important; }}
[class*="st-key-cadstep_"] > [data-testid="stLayoutWrapper"],
[class*="st-key-cadstep_"] > [data-testid="stElementContainer"] {{ width: auto !important; }}
[class*="st-key-cadminus_"] button, [class*="st-key-cadplus_"] button {{
    width: 38px !important; height: 38px !important; min-height: 38px !important;
    border-radius: 4px !important; border: 1px solid {LINE_RAIL} !important;
    padding: 0 !important; justify-content: center !important; }}
[data-testid="stMain"] [class*="st-key-cadminus_"] button p, [data-testid="stMain"] [class*="st-key-cadplus_"] button p {{
    font-family: {SANS} !important; font-size: 16px !important; color: {INK} !important; }}
.cad-stepval {{
    width: 64px; height: 38px; border: 1px solid {PRIMARY_DEEP}; border-radius: 4px;
    background: #FFFFFF; display: flex; align-items: center; justify-content: center;
    font-family: {SANS}; font-weight: 500; font-size: 15px; line-height: 22.5px; color: {INK}; }}

[class*="st-key-cadseg_"] {{
    flex-direction: row !important; gap: 0 !important; align-items: center !important;
    padding-top: 16px !important; }}
[class*="st-key-cadseg_"] > [data-testid="stLayoutWrapper"] {{ width: auto !important; }}
[class*="st-key-cadday_"] button, [class*="st-key-caddaysel_"] button {{
    width: auto !important; min-width: 82px !important; height: 47px !important;
    min-height: 47px !important; border-radius: 0 !important;
    border: 1px solid {LINE_RAIL} !important; padding: 0 20px !important;
    justify-content: center !important; }}
[data-testid="stMain"] [class*="st-key-cadday_"] button p, [data-testid="stMain"] [class*="st-key-caddaysel_"] button p {{
    font-family: {GROTESK} !important; font-size: 14px !important; line-height: 21px !important;
    color: {INK_SOFT} !important; }}
[class*="st-key-caddaysel_"] button {{
    background: {PRIMARY_DEEP} !important; border-color: {PRIMARY_DEEP} !important; }}
[class*="st-key-cadseg_"] > [data-testid="stLayoutWrapper"]:first-child button {{
    border-radius: 8px 0 0 8px !important; }}
[class*="st-key-cadseg_"] > [data-testid="stLayoutWrapper"]:last-child button {{
    border-radius: 0 8px 8px 0 !important; }}
[data-testid="stMain"] [class*="st-key-caddaysel_"] button p {{ color: #FFFFFF !important; font-weight: 500 !important; }}

/* ---------------- subjects ---------------- */
[class*="st-key-cadsub_"] button {{
    width: auto !important; height: 39px !important; min-height: 39px !important;
    border-radius: 10px !important; background: {CHIP_BG} !important;
    border: 1px solid {CHIP_BD} !important; padding: 0 14px !important;
    justify-content: center !important; }}
[data-testid="stMain"] [class*="st-key-cadsub_"] button p {{
    font-family: {GROTESK} !important; font-weight: 400 !important;
    font-size: 14px !important; line-height: 21px !important; color: {INK} !important; }}
[data-testid="stMain"] .stTextInput label {{ display: none !important; }}
[data-testid="stMain"] [data-testid="stTextInputRootElement"] {{
    height: 49px !important; min-height: 49px !important; border-radius: 10px !important;
    border: 1px solid {LINE_RAIL} !important; background: #FFFFFF !important;
    box-shadow: none !important; }}
[data-testid="stMain"] .stTextInput input {{
    font-family: {SANS} !important; font-size: 14px !important; color: {INK} !important;
    padding: 13px 18px !important; height: 47px !important; background: transparent !important; }}
[data-testid="stMain"] .stTextInput input::placeholder {{
    color: rgba(26,26,46,.5) !important; opacity: 1 !important; }}
.st-key-cadsearch {{ padding-top: 20px !important; }}
[class*="st-key-cadsug_"] button {{
    width: auto !important; height: 40px !important; min-height: 40px !important;
    border-radius: 20px !important; border: 1px solid {LINE_RAIL} !important;
    padding: 0 18px !important; justify-content: center !important; }}
[data-testid="stMain"] [class*="st-key-cadsug_"] button p {{
    font-family: {GROTESK} !important; font-weight: 400 !important;
    font-size: 14px !important; line-height: 21px !important; color: {INK_SOFT} !important; }}

/* ---------------- sticky action bar ---------------- */
.st-key-cadbar {{
    position: fixed !important; left: 547px; right: 0; bottom: 0; height: 82px;
    width: auto !important;
    background: {CANVAS}; border-top: 1px solid {LINE};
    flex-direction: row !important; align-items: center !important;
    justify-content: space-between !important; gap: 0 !important;
    padding: 0 32px !important; box-sizing: border-box !important; z-index: 10;
}}
.st-key-cadbar > [data-testid="stLayoutWrapper"] {{ width: auto !important; }}
.st-key-cadback button {{
    width: auto !important; height: 44px !important; min-height: 44px !important;
    border-radius: 8px !important; border: 1px solid {LINE_RAIL} !important;
    padding: 0 24px !important; justify-content: center !important; }}
.st-key-cadback button p {{
    font-family: {SANS} !important; font-weight: 500 !important; font-size: 15px !important;
    color: {INK_SOFT} !important; }}
.st-key-cadnext button {{
    width: auto !important; height: 44px !important; min-height: 44px !important;
    border-radius: 8px !important; background: {PRIMARY} !important;
    border: 1px solid {PRIMARY} !important; padding: 0 32px !important;
    justify-content: center !important; }}
.st-key-cadnext button p {{
    font-family: {SANS} !important; font-weight: 600 !important; font-size: 15px !important;
    line-height: 22.5px !important; color: #FFFFFF !important; }}
.st-key-cadnext button:disabled {{ opacity: .45 !important; }}
.st-key-cadnext button:disabled p {{ color: #FFFFFF !important; }}

/* ---------------- finish screen ---------------- */
.cad-done {{
    position: fixed; inset: 0; background: #F8F8FC; z-index: 5;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 16px; }}
.cad-done h2 {{
    font-family: {SERIF}; font-weight: 400; font-size: 34px; line-height: 41px;
    color: {INK}; margin: 0; }}
.cad-done p {{
    font-family: {GROTESK}; font-weight: 400; font-size: 16px; line-height: 24px;
    color: {MUTED}; margin: 0; }}
.st-key-caddone {{
    position: fixed !important; left: 50%; top: calc(50% + 120px);
    transform: translateX(-50%); z-index: 6; width: auto !important; }}
.st-key-caddone button {{
    width: auto !important; height: 44px !important; min-height: 44px !important;
    border-radius: 8px !important; background: {PRIMARY} !important;
    border: 1px solid {PRIMARY} !important; padding: 0 32px !important;
    justify-content: center !important; }}
.st-key-caddone button p {{
    font-family: {SANS} !important; font-weight: 600 !important; font-size: 15px !important;
    color: #FFFFFF !important; }}
</style>
"""


# ------------------------------------------------------------------ rail
def _steps_html(active):
    rows = []
    for i, label in enumerate(STEPS, start=1):
        cls = 'now' if i == active else ('done' if i < active else 'todo')
        rows.append(f'<div class="cad-step {cls}"><div class="n">{i}</div>'
                    f'<div class="l">{label}</div></div>')
    return f'<div class="cad-rail-steps">{"".join(rows)}</div>'


def _rail(active, body=''):
    st.markdown(
        f'<div class="cad-rail">{brand()}{_steps_html(active)}{body}'
        f'<div class="cad-rail-spacer"></div>'
        f'<p class="cad-rail-foot">Takes about two minutes. You can change any of this later.</p>'
        f'</div>', unsafe_allow_html=True)


def _week_totals():
    r = st.session_state.onboarding["routine"]
    sleep = r["sleep_hours"] * 7
    school = r["school_hours"] * r["school_days"]
    commitments = sum(hrs for key, _, hrs in COMMITMENTS if r.get(key))
    free = max(0, 168 - sleep - school - commitments)
    return sleep, school, commitments, free


def _bar(label, hours):
    pct = min(100, round(hours / 168 * 100))
    return (f'<div class="cad-bar"><div class="row"><span>{label}</span><b>{hours}h</b></div>'
            f'<div class="track"><i style="width:{pct}%"></i></div></div>')


def _live_panel():
    sleep, school, commitments, free = _week_totals()
    bars = (_bar("Sleep", sleep) + _bar("School / college", school)
            + _bar("Commitments", commitments) + _bar("Free for study", free))
    return (f'<div class="cad-live"><h4>Your Week, Live</h4>'
            f'<div class="big"><b>{free}</b><span>free hours / week</span></div>'
            f'<div class="cad-bars">{bars}</div></div>')


def _art_panel():
    return ('<div class="cad-rail-art">' + FOCUS_LOOP + '</div>'
            '<p class="cad-rail-lede">A study system shaped around your real life, '
            'not a generic template</p>')


def _action_bar(next_label="Continue", back_page=None, next_page=None,
                enabled=True, on_next=None):
    with st.container(key="cadbar"):
        with st.container(key="cadback"):
            if back_page is not None:
                if st.button("Back", key="ob_go_back"):
                    st.session_state.page = back_page
                    st.rerun()
            else:
                st.markdown('<div style="width:1px"></div>', unsafe_allow_html=True)
        with st.container(key="cadnext"):
            if st.button(next_label, key="ob_go_next", disabled=not enabled):
                if on_next:
                    on_next()
                if next_page is not None:
                    st.session_state.page = next_page
                st.rerun()


# ------------------------------------------------------------------ step 1
def page_one():
    ob = st.session_state.onboarding
    _rail(1, _art_panel())

    st.markdown('<p class="cad-h1">Let\'s build a study system that works for you.</p>',
                unsafe_allow_html=True)
    st.markdown('<div class="cad-bubble">Hi, before we begin, I\'d love to learn a bit '
                'about you....</div>', unsafe_allow_html=True)
    st.markdown('<p class="cad-q">What best describes you?</p>', unsafe_allow_html=True)

    with st.container(key="cadgrid_type"):
        for i, label in enumerate(STUDENT_TYPES):
            chosen = ob["student_type"] == label
            variant = "sel" if chosen else "opt"
            with st.container(key=f"cad{variant}_type{i}"):
                if st.button(label, key=f"ob_type_{i}"):
                    ob["student_type"] = label
                    st.rerun()

    if ob["student_type"]:
        st.markdown('<div class="cad-bubble">Got it.. I\'ll keep things light and '
                    'motivating.</div>', unsafe_allow_html=True)
        st.markdown('<p class="cad-q">What would you like help with most?</p>',
                    unsafe_allow_html=True)

        with st.container(key="cadgridg_goal"):
            for i, (emoji, label) in enumerate(GOALS):
                chosen = ob["goal"] == label
                variant = "gsel" if chosen else "goal"
                with st.container(key=f"cad{variant}_goal{i}"):
                    if st.button(f"{emoji} {label}", key=f"ob_goal_{i}"):
                        ob["goal"] = label
                        st.rerun()

    _action_bar(next_page=2, enabled=bool(ob["student_type"] and ob["goal"]))


# ------------------------------------------------------------------ step 2
def page_two():
    r = st.session_state.onboarding["routine"]
    _rail(2, _live_panel())

    st.markdown('<p class="cad-h1">Let\'s understand your typical week.</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="cad-lede">This helps us create a realistic study plan that fits '
                'around your life. No schedules — just rough amounts.</p>',
                unsafe_allow_html=True)

    st.markdown(f'<div class="cad-metric"><span>How many hours do you usually sleep?</span>'
                f'<b>{r["sleep_hours"]}hrs</b></div>', unsafe_allow_html=True)
    sleep = st.slider("sleep", 4, 12, r["sleep_hours"], key="ob_sleep",
                      label_visibility="collapsed")
    if sleep != r["sleep_hours"]:
        r["sleep_hours"] = sleep
        st.rerun()

    st.markdown('<p class="cad-q">Hours at school on a typical day?</p>', unsafe_allow_html=True)
    with st.container(key="cadstep_school"):
        with st.container(key="cadminus_school"):
            if st.button("−", key="ob_school_minus"):
                r["school_hours"] = max(0, r["school_hours"] - 1)
                st.rerun()
        st.markdown(f'<div class="cad-stepval">{r["school_hours"]}h</div>',
                    unsafe_allow_html=True)
        with st.container(key="cadplus_school"):
            if st.button("+", key="ob_school_plus"):
                r["school_hours"] = min(12, r["school_hours"] + 1)
                st.rerun()

    st.markdown('<p class="cad-q">How many days per week do you attend?</p>',
                unsafe_allow_html=True)
    custom = r["school_days"] not in (5, 6, 7)
    with st.container(key="cadseg_days"):
        for i, days in enumerate([5, 6, 7]):
            chosen = (not custom) and r["school_days"] == days
            variant = "daysel" if chosen else "day"
            with st.container(key=f"cad{variant}_d{i}"):
                if st.button(f"{days} days", key=f"ob_days_{i}"):
                    r["school_days"] = days
                    st.rerun()
        with st.container(key=("caddaysel_d3" if custom else "cadday_d3")):
            if st.button("Custom", key="ob_days_custom"):
                r["school_days"] = 4 if not custom else r["school_days"]
                st.rerun()
    if custom:
        with st.container(key="cadstep_days"):
            with st.container(key="cadminus_days"):
                if st.button("−", key="ob_days_minus"):
                    r["school_days"] = max(1, r["school_days"] - 1)
                    st.rerun()
            st.markdown(f'<div class="cad-stepval">{r["school_days"]}d</div>',
                        unsafe_allow_html=True)
            with st.container(key="cadplus_days"):
                if st.button("+", key="ob_days_plus"):
                    r["school_days"] = min(7, r["school_days"] + 1)
                    st.rerun()

    st.markdown('<p class="cad-q">What else regularly takes up your time?</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="cad-lede" style="padding-top:4px">Tap to add, adjust the amounts. '
                'Skip anything that doesn\'t apply.</p>', unsafe_allow_html=True)
    with st.container(key="cadrow_commit"):
        for i, (key, label, _hrs) in enumerate(COMMITMENTS):
            on = bool(r.get(key))
            variant = "psel" if on else "pill"
            with st.container(key=f"cad{variant}_c{i}"):
                if st.button(("✓ " if on else "+ ") + label, key=f"ob_commit_{i}"):
                    r[key] = not on
                    st.rerun()

    _action_bar(back_page=1, next_page=3)


# ------------------------------------------------------------------ step 3
def page_three():
    ob = st.session_state.onboarding
    selected = ob["subjects"]
    _rail(3, _live_panel())

    st.markdown('<p class="cad-h1">Let\'s prepare your workspace.</p>', unsafe_allow_html=True)
    st.markdown('<p class="cad-lede">Add the subjects you\'re studying so creating tasks later '
                'takes one tap.\nYou can skip and add them anytime.</p>', unsafe_allow_html=True)

    st.markdown('<p class="cad-q">Your subjects</p>', unsafe_allow_html=True)
    if selected:
        with st.container(key="cadrow_subs"):
            for i, name in enumerate(selected):
                with st.container(key=f"cadsub_s{i}"):
                    if st.button(f"{name}   ×", key=f"ob_rm_{name}"):
                        selected.remove(name)
                        st.rerun()

    with st.container(key="cadsearch"):
        typed = st.text_input("subject", placeholder="Search or type a subject...",
                              key="ob_subject", label_visibility="collapsed")
    if typed:
        clean = typed.strip()
        if clean and clean not in selected:
            selected.append(clean)
            del st.session_state["ob_subject"]
            st.rerun()

    remaining = [s for s in SUGGESTED_SUBJECTS if s not in selected]
    if remaining:
        with st.container(key="cadrow_sug"):
            for i, name in enumerate(remaining):
                with st.container(key=f"cadsug_s{i}"):
                    if st.button(f"+ {name}", key=f"ob_add_{name}"):
                        selected.append(name)
                        st.rerun()

    _action_bar("Finish setup", back_page=2, next_page=4, enabled=len(selected) >= 2)


# ------------------------------------------------------------------ done
def page_four():
    st.markdown(
        '<div class="cad-done">'
        '<svg width="86" height="86" viewBox="0 0 24 24" fill="none" stroke="#5A5AAB" '
        'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.2 2.2M16.9 16.9l2.2 2.2'
        'M19.1 4.9l-2.2 2.2M7.1 16.9l-2.2 2.2"/><circle cx="12" cy="12" r="5"/></svg>'
        '<h2>Your plan is ready</h2>'
        '<p>Lets create your first study task</p>'
        '</div>', unsafe_allow_html=True)

    with st.container(key="caddone"):
        if st.button("Proceed to Cadence", key="ob_finish_setup"):
            user_id = st.session_state.user[0]
            db.save_onboarding_profile(user_id, st.session_state.onboarding)
            for existing in db.get_subjects(user_id):
                db.delete_subject(existing["id"])
            for name in st.session_state.onboarding.get("subjects", []):
                db.add_subject(user_id, name)
            st.session_state.screen = "dashboard"
            st.rerun()


def onboarding():
    st.markdown(CSS, unsafe_allow_html=True)
    page = st.session_state.page
    if page == 1:
        page_one()
    elif page == 2:
        page_two()
    elif page == 3:
        page_three()
    else:
        page_four()
