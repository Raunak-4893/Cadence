"""Cadence — sign in / sign up / reset password screens.

UI is a 1:1 implementation of the `log in/sign up` section of Study_Planner.fig
(frames: `sign In`, `sign up`, `Reset your password`).
"""

import streamlit as st
import database as db
from pages._ui import HIDE_SIDEBAR

# ---------------------------------------------------------------- design tokens
INK = "#1A1A2E"          # headings / input text
MUTED = "#7070A0"        # secondary copy
PRIMARY = "#5A5AAB"      # primary button
PANEL = "#252342"        # left panel background
PANEL_BODY = "#9896C8"   # left panel paragraph
PANEL_DESC = "#7A789E"   # left panel feature description
PANEL_FOOT = "#5E5C8A"   # left panel footer
ICON_BG = "#322F5E"      # left panel feature icon chip
CANVAS = "#FAFAFA"       # right panel background
LINE = "#E4E4EE"         # borders / dividers
REQUIRED = "#EF4444"     # required asterisk

SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
SERIF = "'Newsreader', Georgia, 'Times New Roman', serif"
GROTESK = "'Hanken Grotesk', 'Inter', -apple-system, sans-serif"
DMSANS = "'DM Sans', 'Inter', sans-serif"

LOGO_SVG = """<svg width="27.75" height="30" viewBox="0 0 27.75 30" fill="none" xmlns="http://www.w3.org/2000/svg">
<g transform="matrix(-1,0,0,1,27.75,0)">
<path d="M2.25 4.275 L2.25 25.725 C1.825 25.3 1.425 24.85 1.05 24.375 C0.675 23.9 0.325 23.4125 0 22.9125 L0 7.0875 C0.325 6.5875 0.675 6.1 1.05 5.625 C1.425 5.15 1.825 4.7 2.25 4.275 Z M8.25 0.675 L8.25 29.325 C7.725 29.15 7.2125 28.9563 6.7125 28.7438 C6.2125 28.5313 5.725 28.2875 5.25 28.0125 L5.25 1.9875 C5.725 1.7125 6.2125 1.4688 6.7125 1.2563 C7.2125 1.0438 7.725 0.85 8.25 0.675 Z M18.75 28.7625 L18.75 1.2375 C21.4 2.4125 23.5625 4.225 25.2375 6.675 C26.9125 9.125 27.75 11.9 27.75 15 C27.75 18.1 26.9125 20.875 25.2375 23.325 C23.5625 25.775 21.4 27.5875 18.75 28.7625 Z M12.75 30 C12.5 30 12.25 29.9938 12 29.9813 C11.75 29.9688 11.5 29.95 11.25 29.925 L11.25 0.075 C11.5 0.05 11.75 0.0312 12 0.0188 C12.25 0.0063 12.5 0 12.75 0 C13.25 0 13.75 0.025 14.25 0.075 C14.75 0.125 15.25 0.2 15.75 0.3 L15.75 29.7 C15.25 29.8 14.75 29.875 14.25 29.925 C13.75 29.975 13.25 30 12.75 30 Z" fill="#FFFFFF"/>
</g></svg>"""

_ICON_ATTRS = ('fill="none" stroke="%s" stroke-width="1.3333" '
               'stroke-linecap="round" stroke-linejoin="round"') % PANEL_BODY

ICON_CALENDAR = ("""<svg width="16" height="16" viewBox="0 0 16 16" %s xmlns="http://www.w3.org/2000/svg">
<rect x="2" y="2.6667" width="12" height="12" rx="1.3333"/>
<path d="M5.3333 1.3333V4M10.6667 1.3333V4M2 6.6667H14"/></svg>""" % _ICON_ATTRS)

ICON_BARS = ("""<svg width="16" height="16" viewBox="0 0 16 16" %s xmlns="http://www.w3.org/2000/svg">
<path d="M12 13.3333V6.6667M8 13.3333V2.6667M4 13.3333V9.3333"/></svg>""" % _ICON_ATTRS)

ICON_SLIDERS = ("""<svg width="16" height="16" viewBox="0 0 16 16" %s xmlns="http://www.w3.org/2000/svg">
<path d="M7.3333 4.6667H13.3333M3.3333 11.3333H9.3333"/>
<circle cx="4.6667" cy="4.6667" r="2"/><circle cx="11.3333" cy="11.3333" r="2"/></svg>""" % _ICON_ATTRS)


def _feature(icon, title, body):
    return f"""<div class="cad-feature">
      <div class="cad-feature-icon">{icon}</div>
      <div class="cad-feature-copy">
        <div class="cad-feature-title">{title}</div>
        <div class="cad-feature-body">{body}</div>
      </div>
    </div>"""


LEFT_PANEL = f"""
<div class="cad-left">
  <div class="cad-brand">{LOGO_SVG}<span>Cadence</span></div>
  <h1 class="cad-hero">Plan smarter.<br/>Study better.</h1>
  <p class="cad-lede">An adaptive study planner that builds your personal timetable,
     tracks your progress, and quietly adjusts when life gets in the way.</p>
  <div class="cad-features">
    {_feature(ICON_CALENDAR, "Adaptive timetable",
              "Redistributes tasks automatically around your real availability and priorities.")}
    {_feature(ICON_BARS, "Progress tracking",
              "See subject progress, weekly completion, and what's coming up — at a glance.")}
    {_feature(ICON_SLIDERS, "Smart scheduling",
              "Priority sorting and gentle workload balancing keep your week realistic.")}
  </div>
  <div class="cad-spacer"></div>
  <div class="cad-foot">&copy; 2026 Cadence &middot; Built for students</div>
</div>
"""

CSS = f"""
<style>
{HIDE_SIDEBAR}
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&family=Hanken+Grotesk:wght@400;500;600&family=Inter:wght@400;500;600;700&family=Newsreader:wght@600;700;800&display=swap');

/* ---------- strip Streamlit chrome ---------- */
header[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
#MainMenu, footer {{ display: none !important; }}
[data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
    background: {CANVAS} !important; }}

/* ---------- page shell: fixed 440px panel + centred 360px form ---------- */
[data-testid="stMainBlockContainer"] {{
    padding: 0 !important;
    max-width: none !important;
    margin-left: 440px !important;
    width: calc(100% - 440px) !important;
    min-height: 100vh !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
    flex: 0 0 360px !important; width: 360px !important; max-width: 360px !important;
}}
[data-testid="stMain"] [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
[data-testid="stMain"] [data-testid="stLayoutWrapper"] {{ width: 100% !important; }}
/* Streamlit offsets markdown blocks by -1rem; we set our own margins instead */
[data-testid="stMarkdown"] > div > [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}

/* ---------- left panel ---------- */
.cad-left {{
    position: fixed; top: 0; left: 0; bottom: 0;
    width: 440px; height: 100vh;
    background: {PANEL};
    padding: 36px 44px 28px 44px;
    display: flex; flex-direction: column;
    box-sizing: border-box; z-index: 9;
}}
.cad-brand {{ display: flex !important; align-items: center; gap: 8px; height: 30px; }}
.cad-brand span {{
    font-family: {SERIF} !important; font-weight: 600 !important; font-size: 15px !important;
    line-height: 22.5px !important; color: #FFFFFF !important;
}}
.cad-hero {{
    margin: 52px 0 0 0 !important; padding: 0 !important;
    font-family: {SERIF} !important; font-weight: 800 !important; font-size: 42px !important;
    line-height: 47.04px !important; color: #FFFFFF !important; letter-spacing: 0 !important;
    height: 95px;
}}
.cad-lede {{
    margin: 20px 0 0 0 !important; width: 330px !important; max-width: 330px !important;
    font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 14px !important;
    line-height: 23.1px !important; color: {PANEL_BODY} !important;
    height: 70px;
}}
.cad-features {{ margin-top: 48px; display: flex; flex-direction: column; gap: 28px; }}
.cad-feature {{ display: flex; gap: 12px; align-items: flex-start; }}
.cad-feature-icon {{
    flex: 0 0 32px; width: 32px; height: 32px; margin-top: 1px;
    border-radius: 10px; background: {ICON_BG};
    display: flex; align-items: center; justify-content: center;
}}
.cad-feature-title {{
    font-family: {SANS} !important; font-weight: 600 !important; font-size: 14px !important;
    line-height: 21px !important; color: #FFFFFF !important;
}}
.cad-feature-body {{
    margin-top: 3px;
    font-family: {SANS} !important; font-weight: 400 !important; font-size: 13px !important;
    line-height: 20.15px !important; color: {PANEL_DESC} !important;
    min-height: 41px;
}}
.cad-spacer {{ flex: 1 1 auto; min-height: 24px; }}
.cad-foot {{
    font-family: {SANS} !important; font-weight: 400 !important; font-size: 12px !important;
    line-height: 18px !important; color: {PANEL_FOOT} !important;
}}

/* ---------- right panel typography ---------- */
.cad-h1 {{ font-family: {SANS} !important; font-weight: 700 !important; font-size: 32px !important;
          line-height: 48px !important; color: {INK} !important; margin: 0 !important; }}
.cad-h1-serif {{ font-family: {SERIF} !important; font-weight: 700 !important; font-size: 28px !important;
          line-height: 42px !important; color: {INK} !important; margin: 0 !important; }}
.cad-sub {{ font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 14px !important;
          line-height: 21px !important; color: {MUTED} !important; margin: 0 !important;
          padding-top: 8px !important; }}
.cad-sub-6 {{ padding-top: 6px !important; }}
.cad-label {{ font-family: {GROTESK} !important; font-weight: 500 !important; font-size: 13px !important;
          line-height: 19.5px !important; color: {INK} !important; margin: 0 !important; }}
.cad-label i {{ color: {REQUIRED} !important; font-style: normal !important; }}
.cad-terms {{ font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 12px !important;
          line-height: 18px !important; color: #9898B8 !important; margin: 0 !important;
          padding-top: 10px !important; }}

/* ---------- text inputs ---------- */
[data-testid="stMain"] .stTextInput label,
[data-testid="stDialog"] .stTextInput label {{ display: none !important; }}
[data-testid="stTextInputRootElement"] {{
    height: 47px !important; min-height: 47px !important;
    border-radius: 10px !important;
    border: 1px solid {LINE} !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
}}
[data-testid="stTextInputRootElement"]:focus-within {{ border-color: {PRIMARY} !important; }}
[data-testid="stTextInputRootElement"] input {{
    font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 14px !important;
    color: {INK} !important; padding: 12px 14px !important; height: 45px !important;
    background: transparent !important; -webkit-text-fill-color: {INK} !important;
}}
[data-testid="stTextInputRootElement"] input::placeholder {{
    color: rgba(26,26,46,0.5) !important;
    -webkit-text-fill-color: rgba(26,26,46,0.5) !important; opacity: 1 !important; }}
/* password reveal -> "Show" */
[data-testid="stTextInputRootElement"] button {{
    background: transparent !important; border: none !important;
    margin: 0 14px 0 0 !important; padding: 0 !important; width: auto !important;
    min-width: 0 !important; min-height: 0 !important; height: 20px !important;
    box-shadow: none !important;
}}
[data-testid="stTextInputRootElement"] button > span,
[data-testid="stTextInputRootElement"] button [data-testid="stIconMaterial"] {{
    display: none !important; }}
[data-testid="stTextInputRootElement"] button::after {{
    content: "Show";
    font-family: {SANS}; font-weight: 500; font-size: 13px; line-height: 19.5px;
    color: {MUTED};
}}
[data-testid="stTextInputRootElement"] button[aria-pressed="true"]::after {{ content: "Hide"; }}

/* ---------- buttons ---------- */
[data-testid="stMain"] .stButton > button,
[data-testid="stDialog"] .stButton > button {{
    width: 100% !important;
    height: 47px !important; min-height: 47px !important;
    border-radius: 10px !important;
    border: 1px solid {LINE} !important;
    background: #FFFFFF !important;
    color: {INK} !important;
    box-shadow: none !important;
    padding: 0 14px !important;
}}
[data-testid="stMain"] .stButton > button p,
[data-testid="stDialog"] .stButton > button p {{
    font-family: {SANS} !important; font-weight: 500 !important;
    font-size: 14px !important; line-height: 21px !important; color: {INK} !important;
}}
[data-testid="stMain"] .stButton > button:hover {{
    border-color: #D4D4E4 !important; background: #FCFCFF !important; }}

/* primary button */
[data-testid="stMain"] .st-key-cad_primary button,
[data-testid="stDialog"] .st-key-cad_primary button {{
    height: 48.5px !important; min-height: 48.5px !important;
    background: {PRIMARY} !important; border: 1px solid {PRIMARY} !important;
}}
[data-testid="stMain"] .st-key-cad_primary button p,
[data-testid="stDialog"] .st-key-cad_primary button p {{
    font-family: {SANS} !important; font-weight: 600 !important;
    font-size: 15px !important; line-height: 22.5px !important; color: #FFFFFF !important;
}}
[data-testid="stMain"] .st-key-cad_primary button:hover {{
    background: #50509B !important; border-color: #50509B !important; }}

.st-key-cad_secondary {{ padding-top: 10.5px !important; }}
[data-testid="stMain"] .st-key-cad_secondary button p,
[data-testid="stDialog"] .st-key-cad_secondary button p {{ color: #3A3A5C !important; }}

/* ---------- remember-me / forgot row ---------- */
[data-testid="stMain"] .st-key-cad_row {{
    flex-direction: row !important; align-items: center !important;
    justify-content: space-between !important; gap: 0 !important;
    padding-top: 16px !important; padding-bottom: 24px !important; height: 20px !important;
    box-sizing: content-box !important;
}}
[data-testid="stMain"] .st-key-cad_row > [data-testid="stLayoutWrapper"] {{
    width: auto !important; height: 20px !important; }}
[data-testid="stMain"] .st-key-cad_remember,
[data-testid="stMain"] .st-key-cad_forgot {{ height: 20px !important; }}
[data-testid="stMain"] .st-key-cad_remember [data-testid="stElementContainer"],
[data-testid="stMain"] .st-key-cad_forgot [data-testid="stElementContainer"] {{
    height: 20px !important; }}
[data-testid="stMain"] .st-key-cad_forgot .stButton {{
    display: flex !important; align-items: flex-start !important; height: 20px !important; }}
[data-testid="stMain"] .st-key-cad_forgot button {{ height: 19.5px !important; }}
[data-testid="stMain"] .st-key-cad_remember .stCheckbox {{
    height: 20px !important; min-height: 20px !important; }}
[data-testid="stMain"] .st-key-cad_remember label > div:not([data-testid]) {{
    background-color: #FFFFFF !important; border: 1px solid #C9C9DA !important; }}
[data-testid="stMain"] .st-key-cad_remember label:has(input:checked) > div:not([data-testid]) {{
    background-color: {PRIMARY} !important; border-color: {PRIMARY} !important; }}
.st-key-cad_remember p {{
    font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 13px !important; line-height: 19.5px !important; color: #3A3A5C !important;
    margin: 0 !important;
}}
.st-key-cad_remember label {{ gap: 8px !important; align-items: center !important; }}
.st-key-cad_remember label > div:not([data-testid]) {{
    width: 15px !important; height: 15px !important; min-width: 15px !important;
    border-radius: 4px !important; }}
[data-testid="stMain"] .st-key-cad_forgot button,
[data-testid="stMain"] .st-key-cad_signup button,
[data-testid="stDialog"] .st-key-cad_resend button {{
    background: transparent !important; border: none !important;
    height: auto !important; min-height: 0 !important; width: auto !important;
    padding: 0 !important;
}}
[data-testid="stMain"] .st-key-cad_forgot button:hover,
[data-testid="stMain"] .st-key-cad_signup button:hover,
[data-testid="stDialog"] .st-key-cad_resend button:hover {{ background: transparent !important; border: none !important; }}
[data-testid="stMain"] .st-key-cad_forgot button p {{
    font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 13px !important; line-height: 19.5px !important; color: #3D3660 !important;
}}

/* ---------- "Don't have an account? Sign up" ---------- */
[data-testid="stMain"] .st-key-cad_signup_row {{
    flex-direction: row !important; align-items: baseline !important;
    justify-content: center !important; gap: 6px !important; padding-top: 18px !important;
}}
[data-testid="stMain"] .st-key-cad_signup_row {{ height: 24px !important; }}
[data-testid="stMain"] .st-key-cad_signup_row > [data-testid="stLayoutWrapper"] {{
    width: auto !important; height: 24px !important; }}
[data-testid="stMain"] .st-key-cad_signup_row > [data-testid="stElementContainer"] {{
    width: auto !important; height: 19.5px !important; }}
[data-testid="stMain"] .st-key-cad_signup {{ height: 24px !important; }}
[data-testid="stMain"] .st-key-cad_signup [data-testid="stElementContainer"] {{
    height: 24px !important; }}
p.cad-have {{
    font-family: {GROTESK} !important; font-weight: 400 !important; font-size: 13px !important;
    line-height: 19.5px !important; color: {MUTED} !important; margin: 0 !important;
    white-space: nowrap;
}}
[data-testid="stMain"] .st-key-cad_signup button p {{
    font-family: {SANS} !important; font-weight: 600 !important;
    font-size: 16px !important; line-height: 24px !important; color: #3D3660 !important;
    white-space: nowrap;
}}

/* ---------- reset-password dialog ---------- */
[data-testid="stDialog"] {{
    display: flex !important; align-items: center !important; justify-content: center !important;
    background: rgba(20,18,40,0.45) !important;
}}
[data-testid="stDialog"] > div {{ width: auto !important; height: auto !important; }}
[data-testid="stDialog"] section[role="dialog"] {{
    width: 420px !important; max-width: 420px !important; min-width: 0 !important;
    border-radius: 16px !important; background: #FFFFFF !important;
    padding: 32px 32px 28px 32px !important;
    box-shadow: 0 24px 64px rgba(0,0,0,0.18) !important;
}}
[data-testid="stDialog"] section[role="dialog"] > div {{ padding: 0 !important; }}
[data-testid="stDialog"] h2 {{ display: none !important; }}
[data-testid="stDialog"] section[role="dialog"] > button[aria-label="Close"] {{
    top: 16px !important; right: 16px !important; color: #9898B8 !important;
    background: transparent !important; border: none !important; }}
[data-testid="stDialog"] [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
[data-testid="stDialog"] [data-testid="stLayoutWrapper"] {{ width: 100% !important; }}
.cad-h3 {{ font-family: {SANS} !important; font-weight: 700 !important; font-size: 22px !important;
          line-height: 33px !important; color: {INK} !important; margin: 0 !important; }}
.cad-modal-p {{ font-family: {SANS} !important; font-weight: 400 !important; font-size: 13px !important;
          line-height: 20.8px !important; color: {MUTED} !important; margin: 0 !important;
          padding-top: 10px !important; }}
[data-testid="stDialog"] .st-key-cad_resend {{
    padding-top: 25.5px !important; padding-bottom: 5.5px !important;
    align-items: center !important; gap: 0 !important; }}
[data-testid="stDialog"] .st-key-cad_resend > [data-testid="stLayoutWrapper"],
[data-testid="stDialog"] .st-key-cad_resend > [data-testid="stElementContainer"] {{
    width: auto !important; height: 20px !important; }}
[data-testid="stDialog"] .st-key-cad_resend .stButton {{
    height: 20px !important; display: flex !important; align-items: flex-start !important; }}
[data-testid="stDialog"] .st-key-cad_resend button {{
    background: transparent !important; border: none !important;
    height: 20px !important; min-height: 0 !important; width: auto !important;
    padding: 0 !important; }}
[data-testid="stDialog"] .st-key-cad_resend button:hover {{
    background: transparent !important; border: none !important; }}
[data-testid="stDialog"] .st-key-cad_resend button p {{
    font-family: {DMSANS} !important; font-weight: 500 !important;
    font-size: 14px !important; line-height: 20px !important; color: {PRIMARY} !important; }}
[data-testid="stDialog"] .st-key-cad_primary_modal button {{
    height: 48.5px !important; min-height: 48.5px !important;
    background: {PRIMARY} !important; border: 1px solid {PRIMARY} !important; }}
[data-testid="stDialog"] .st-key-cad_primary_modal button p {{
    font-family: {SANS} !important; font-weight: 600 !important;
    font-size: 15px !important; line-height: 22.5px !important; color: #FFFFFF !important; }}
[data-testid="stDialog"] .st-key-cad_secondary_modal {{ padding-top: 10.5px !important; }}
[data-testid="stDialog"] .st-key-cad_secondary_modal button p {{ color: #3A3A5C !important; }}

/* ---------- spacing helpers ---------- */
.cad-mt-32 {{ padding-top: 32px !important; }}
.cad-mt-28 {{ padding-top: 28px !important; }}
.cad-mt-18 {{ padding-top: 18px !important; }}
.cad-mt-16 {{ padding-top: 16px !important; }}
.cad-mt-14 {{ padding-top: 14px !important; }}
.cad-mt-24 {{ padding-top: 24px !important; }}
[class*="st-key-cad_input_"] {{ padding-top: 6px !important; }}
.st-key-cad_input_lg_signup_password input::placeholder {{ font-family: {SANS} !important; }}
[data-testid="stAlertContainer"] {{ margin-top: 14px !important; border-radius: 10px !important; }}
[data-testid="stAlertContainer"] p {{
    font-family: {GROTESK} !important; font-size: 13px !important; line-height: 19.5px !important; }}
</style>
"""


# ------------------------------------------------------------------ helpers
def _init_login_state():
    if "login_page" not in st.session_state:
        st.session_state.login_page = "signin"


def _css():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(LEFT_PANEL, unsafe_allow_html=True)


def _label(text, required=True, cls=""):
    star = ' <i>*</i>' if required else ''
    st.markdown(f'<p class="cad-label {cls}">{text}{star}</p>', unsafe_allow_html=True)


def _field(label, *, key, placeholder, password=False, required=True, top="cad-mt-18"):
    _label(label, required=required, cls=top)
    with st.container(key=f"cad_input_{key}"):
        return st.text_input(
            label, placeholder=placeholder, key=key,
            type="password" if password else "default",
            label_visibility="collapsed",
        )


def _load_onboarding_from_db(user_id):
    """Load saved onboarding profile + subjects into session_state."""
    profile = db.get_onboarding_profile(user_id)
    if not profile:
        return False

    subjects = db.get_subjects(user_id)

    st.session_state.onboarding = {
        "student_type": profile["student_type"],
        "goal": profile["goal"],
        "routine": {
            "sleep_hours": profile["sleep_hours"],
            "school_hours": profile["school_hours"],
            "school_days": profile["school_days"],
            "gym": bool(profile["gym"]),
            "sports": bool(profile["sports"]),
            "coaching": bool(profile["coaching"]),
            "commute": bool(profile["commute"]),
            "part_time": bool(profile["part_time"]),
            "family": bool(profile["family"]),
            "extracurricular": bool(profile["extracurricular"]),
            "weekend_enabled": bool(profile.get("weekend_enabled", True)),
        },
        "subjects": [s["name"] for s in subjects],
    }
    return True


# ------------------------------------------------------------------ dialog
@st.dialog("Reset your password")
def _forgot_password_dialog():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<p class="cad-h3">Reset your password</p>', unsafe_allow_html=True)
    st.markdown('<p class="cad-modal-p">Enter the email or phone linked to your account and '
                "we'll send you a secure link to set a new password.</p>",
                unsafe_allow_html=True)

    _label("Email or phone", cls="cad-mt-24")
    with st.container(key="cad_input_lg_reset_email"):
        email = st.text_input("Email or phone", placeholder="you@email.com",
                              key="lg_reset_email", label_visibility="collapsed")

    with st.container(key="cad_resend"):
        st.button("Re-send Verification Link", key="lg_resend_link")

    with st.container(key="cad_primary_modal"):
        if st.button("Send reset link", key="lg_send_reset", use_container_width=True):
            db.email_exists(email)
            st.success("If that email exists, a reset link has been sent.")

    with st.container(key="cad_secondary_modal"):
        if st.button("Back to sign in", key="lg_reset_back", use_container_width=True):
            st.rerun()


# ------------------------------------------------------------------ screens
def _signin():
    st.markdown('<p class="cad-h1">Welcome back</p>', unsafe_allow_html=True)
    st.markdown('<p class="cad-sub">Sign in to pick up right where you left off.</p>',
                unsafe_allow_html=True)

    email = _field("Email or phone", key="lg_signin_email", placeholder="you@email.com",
                   top="cad-mt-32")
    password = _field("Password", key="lg_signin_password", placeholder="Enter your password",
                      password=True, top="cad-mt-16")

    with st.container(key="cad_row"):
        with st.container(key="cad_remember"):
            st.checkbox("Remember me", key="lg_remember_me")
        with st.container(key="cad_forgot"):
            if st.button("Forgot password?", key="lg_forgot_pw"):
                _forgot_password_dialog()

    with st.container(key="cad_primary"):
        submitted = st.button("Sign in", key="lg_do_signin", use_container_width=True)

    if "signup_success_email" in st.session_state:
        st.success("Account created! Please sign in with your new credentials.")
        del st.session_state["signup_success_email"]

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
        else:
            user = db.verify_user(email, password)
            if user:
                st.session_state.user = user
                if st.session_state.get("lg_remember_me"):
                    st.query_params["cad_uid"] = str(user[0])
                has_profile = _load_onboarding_from_db(user[0])
                st.session_state.screen = "dashboard" if has_profile else "onboarding"
                st.rerun()
            else:
                st.error("Incorrect email or password.")

    with st.container(key="cad_signup_row"):
        st.markdown('<p class="cad-have">Don\'t have an account?</p>', unsafe_allow_html=True)
        with st.container(key="cad_signup"):
            if st.button("Sign up", key="lg_go_signup"):
                st.session_state.login_page = "signup"
                st.rerun()


def _signup():
    st.markdown('<p class="cad-h1-serif">Create your account</p>', unsafe_allow_html=True)
    st.markdown('<p class="cad-sub cad-sub-6">Two minutes to a calmer, more realistic study week.</p>',
                unsafe_allow_html=True)

    name = _field("Your name", key="lg_signup_name", placeholder="Aarav Sharma",
                  top="cad-mt-28")
    email = _field("Email address", key="lg_signup_email", placeholder="you@email.com",
                   top="cad-mt-14")
    password = _field("Password", key="lg_signup_password", placeholder="At least 8 characters",
                      password=True, top="cad-mt-14")

    st.markdown('<p class="cad-terms">By creating an account you agree to our Terms and '
                'Privacy Policy.</p>', unsafe_allow_html=True)
    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)

    with st.container(key="cad_primary"):
        created = st.button("Create account", key="lg_do_signup", use_container_width=True)

    with st.container(key="cad_secondary"):
        if st.button("Back to sign in", key="lg_back_signin", use_container_width=True):
            st.session_state.login_page = "signin"
            st.rerun()

    if created:
        if not name or not email or not password:
            st.error("Please fill in all fields.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            success, message = db.create_user(name, email, password)
            if success:
                st.session_state.login_page = "signin"
                st.session_state.signup_success_email = email
                st.rerun()
            else:
                st.error(message)


def _restore_remembered_session():
    """Re-attach a 'Remember me' session after a browser refresh.

    Streamlit clears session_state on refresh, so the signed-in user id is kept
    in the URL query string (which survives) and swapped back for a real session
    here. app.py's Log out clears the query string, so this cannot resurrect a
    session the user deliberately ended.
    """
    if st.session_state.get("user"):
        return
    uid = st.query_params.get("cad_uid")
    if not uid:
        return
    try:
        user = db.get_user_by_id(int(uid))
    except (TypeError, ValueError):
        user = None
    if not user:
        st.query_params.clear()
        return
    st.session_state.user = user
    st.session_state.screen = "dashboard" if _load_onboarding_from_db(user[0]) else "onboarding"
    st.rerun()


def login():
    _restore_remembered_session()
    _init_login_state()
    _css()
    if st.session_state.login_page == "signin":
        _signin()
    else:
        _signup()
