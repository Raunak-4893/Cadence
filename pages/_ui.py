"""Shared design tokens + chrome for the Cadence UI (from Study_Planner.fig)."""

import streamlit as st

# ---------------------------------------------------------------- palette
INK = "#1A1A2E"
INK_SOFT = "#3A3A5C"
MUTED = "#7070A0"
FAINT = "#9898B8"
PRIMARY = "#5A5AAB"
PRIMARY_DEEP = "#3D3660"
PRIMARY_MID = "#5A5490"
RAIL = "#E8E8F2"
CANVAS = "#FAFAFA"
LINE = "#E4E4EE"
LINE_RAIL = "#DDDDE8"
BAR_TRACK = "#D8D8E8"
BAR_FILL = "#8880C8"
CHIP_BG = "#EDEDFD"
CHIP_BD = "#CBCBE8"
SEL_BG = "#DDDDF0"
SEL_BD = "#A0A0C8"

SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
SERIF = "'Newsreader', Georgia, 'Times New Roman', serif"
GROTESK = "'Hanken Grotesk', 'Inter', -apple-system, sans-serif"

FONT_IMPORT = ("@import url('https://fonts.googleapis.com/css2?"
               "family=DM+Sans:wght@400;500&family=Hanken+Grotesk:wght@400;500;600;700"
               "&family=Inter:wght@400;500;600;700&family=Newsreader:wght@400;600;700;800"
               "&display=swap');")

LOGO_PATH = (
    "M2.25 4.275 L2.25 25.725 C1.825 25.3 1.425 24.85 1.05 24.375 C0.675 23.9 0.325 23.4125 0 22.9125 "
    "L0 7.0875 C0.325 6.5875 0.675 6.1 1.05 5.625 C1.425 5.15 1.825 4.7 2.25 4.275 Z "
    "M8.25 0.675 L8.25 29.325 C7.725 29.15 7.2125 28.9563 6.7125 28.7438 C6.2125 28.5313 5.725 28.2875 "
    "5.25 28.0125 L5.25 1.9875 C5.725 1.7125 6.2125 1.4688 6.7125 1.2563 C7.2125 1.0438 7.725 0.85 "
    "8.25 0.675 Z M18.75 28.7625 L18.75 1.2375 C21.4 2.4125 23.5625 4.225 25.2375 6.675 C26.9125 9.125 "
    "27.75 11.9 27.75 15 C27.75 18.1 26.9125 20.875 25.2375 23.325 C23.5625 25.775 21.4 27.5875 "
    "18.75 28.7625 Z M12.75 30 C12.5 30 12.25 29.9938 12 29.9813 C11.75 29.9688 11.5 29.95 11.25 29.925 "
    "L11.25 0.075 C11.5 0.05 11.75 0.0312 12 0.0188 C12.25 0.0063 12.5 0 12.75 0 C13.25 0 13.75 0.025 "
    "14.25 0.075 C14.75 0.125 15.25 0.2 15.75 0.3 L15.75 29.7 C15.25 29.8 14.75 29.875 14.25 29.925 "
    "C13.75 29.975 13.25 30 12.75 30 Z")


LOGO_URI = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='27.75' height='30' viewBox='0 0 27.75 30'>"
    "<g transform='matrix(-1,0,0,1,27.75,0)'><path fill='%235A5AAB' d='"
    + LOGO_PATH.replace("#", "%23") + "'/></g></svg>")


def logo_svg(color=PRIMARY, w=27.75, h=30):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 27.75 30" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg"><g transform="matrix(-1,0,0,1,27.75,0)">'
            f'<path d="{LOGO_PATH}" fill="{color}"/></g></svg>')


def brand(color=PRIMARY):
    return (f'<div class="cad-brand">{logo_svg(color)}'
            f'<span style="color:{color}">Cadence</span></div>')


# Chrome that every Cadence screen shares: kill Streamlit's header/padding and
# make the page a full-bleed 100vh canvas.
BASE_CSS = f"""
{FONT_IMPORT}
/* Hide the header's contents but keep the header itself: Streamlit mounts the
   "expand sidebar" arrow inside it, and display:none would strand a collapsed
   sidebar with no way to bring it back. */
header[data-testid="stHeader"] {{
    background: transparent !important; height: 0 !important; min-height: 0 !important;
    pointer-events: none !important; }}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
#MainMenu, footer, [data-testid="stSidebarNav"] {{ display: none !important; }}
[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important; visibility: visible !important; opacity: 1 !important;
    pointer-events: auto !important; z-index: 1000 !important; }}
[data-testid="stSidebarCollapsedControl"] * {{ pointer-events: auto !important; }}
/* The design has a permanent sidebar, and Streamlit's collapsed state can strand
   the user with no way back, so the collapse arrow is removed entirely. */
[data-testid="stSidebar"] button[kind="headerNoPadding"],
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
[data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
    background: {CANVAS} !important; }}
[data-testid="stMainBlockContainer"] {{
    padding: 0 !important; max-width: none !important; }}
[data-testid="stMain"] [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
[data-testid="stMarkdown"] > div > [data-testid="stMarkdownContainer"] {{
    margin-bottom: 0 !important; }}
.cad-brand {{ display: flex !important; align-items: center; gap: 8px; height: 30px; }}
.cad-brand span {{
    font-family: {SERIF} !important; font-weight: 600 !important;
    font-size: 15px !important; line-height: 22.5px !important; }}
"""


# Login / onboarding run without any sidebar at all.
HIDE_SIDEBAR = """
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
    display: none !important; }
"""

# Styles Streamlit's own sidebar (the one app.py fills via render_custom_sidebar)
# to match the sidebar in the Figma frames, without changing app.py.
SIDEBAR_CSS = f"""
/* Force the sidebar open no matter what collapsed state the browser remembered.
   Streamlit hides it with a transform / negative margin / zero width, so every
   one of those is overridden here. */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="false"],
div[data-testid="stSidebar"],
div[data-testid="stSidebar"][aria-expanded="false"] {{
    display: block !important; visibility: visible !important; opacity: 1 !important;
    transform: none !important; margin-left: 0 !important; left: 0 !important;
    width: 250px !important; min-width: 250px !important; max-width: 250px !important;
    position: relative !important; }}
[data-testid="stSidebar"] > div {{
    transform: none !important; width: 250px !important; min-width: 250px !important; }}
[data-testid="stSidebarContent"] {{ width: 250px !important; }}
/* keep the collapse/expand arrow clickable above our fixed page chrome */
[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important; visibility: visible !important; opacity: 1 !important;
    z-index: 1000 !important; }}
[data-testid="stSidebar"] {{
    background: #FFFFFF !important; border-right: 1px solid {LINE_RAIL} !important;
    width: 250px !important; min-width: 250px !important; }}
[data-testid="stSidebar"] > div {{ padding-top: 8px !important; }}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding: 16px 16px 16px 16px !important; }}
[data-testid="stSidebar"] .sidebar-title {{ display: none !important; }}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    position: relative !important; padding-top: 64px !important; }}
[data-testid="stSidebar"] .st-key-ui_logo_home {{
    order: -1 !important; position: absolute !important; top: 6px; left: 16px;
    width: calc(100% - 32px) !important; margin: 0 !important; }}
[data-testid="stSidebar"] .st-key-ui_logo_home .stButton > button {{
    background: transparent !important; border: none !important; box-shadow: none !important;
    height: 40px !important; min-height: 40px !important; padding: 0 !important;
    justify-content: flex-start !important; }}
[data-testid="stSidebar"] .st-key-ui_logo_home .stButton > button:hover {{
    background: transparent !important; }}
[data-testid="stSidebar"] .st-key-ui_logo_home .stButton > button p {{
    font-family: {SERIF} !important; font-weight: 600 !important; font-size: 24px !important;
    line-height: 30px !important; color: {PRIMARY} !important; }}
[data-testid="stSidebar"] .st-key-ui_logo_home .stButton > button p::before {{
    content: ""; display: inline-block; width: 26px; height: 28px; margin-right: 8px;
    vertical-align: -6px; background-repeat: no-repeat; background-size: contain;
    background-image: url("data:image/svg+xml;utf8,{LOGO_URI}"); }}
[data-testid="stSidebar"] .sidebar-title-unused {{
    font-family: {SERIF} !important; font-weight: 600 !important; font-size: 24px !important;
    line-height: 30px !important; color: {PRIMARY} !important;
    padding: 8px 0 24px 0 !important; }}
[data-testid="stSidebar"] .stButton > button {{
    width: 100% !important; height: 36px !important; min-height: 36px !important;
    border-radius: 10px !important; border: none !important;
    background: transparent !important; box-shadow: none !important;
    justify-content: flex-start !important; padding: 0 12px !important; }}
[data-testid="stSidebar"] .stButton > button > div {{
    width: 100% !important; justify-content: flex-start !important; }}
[data-testid="stSidebar"] .stButton > button p {{
    font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 14px !important; line-height: 20px !important; color: #6B6B85 !important; }}
[data-testid="stSidebar"] .stButton > button:hover {{ background: {RAIL} !important; }}
[data-testid="stSidebar"] [data-testid="stElementContainer"] {{ margin-bottom: 8px !important; }}
[data-testid="stSidebar"] hr {{ border-color: {LINE_RAIL} !important; }}
"""


# ---------------------------------------------------------------- zoom / viewport
# Browser zoom changes the size of the CSS viewport, so nothing may depend on the
# page being a particular width or the screen being a particular height. These
# rules are appended LAST on every screen so they win over the fixed sizes above.
RESPONSIVE_CSS = f"""
[data-testid="stAppViewContainer"] {{ overflow-x: hidden !important; }}
[data-testid="stMain"] {{ overflow-y: auto !important; }}
[data-testid="stMainBlockContainer"] {{
    max-width: 100% !important; box-sizing: border-box !important; }}

/* Pop-ups must never grow past the screen. Without this the task menu runs off
   the bottom of the viewport at 100% zoom and "Move task" / "Remove task" can't
   be reached at all — the whole reason the app only worked zoomed out to 60%. */
/* `html body div…` on purpose: Streamlit injects its own 92vh cap from a
   runtime-generated stylesheet that lands after this one, so an equally
   specific rule would lose the tie no matter how many !importants it carries. */
html body div[data-testid="stDialog"] div[role="dialog"] {{
    max-height: 90vh !important; overflow-y: auto !important;
    max-width: min(96vw, 640px) !important; box-sizing: border-box !important; }}
/* after the dialog rule on purpose: a popover is also role="dialog", and the
   two selectors carry the same specificity, so source order breaks the tie. */
html body div[data-testid="stPopoverBody"] {{
    max-height: min(68vh, 520px) !important;
    max-width: min(94vw, 380px) !important;
    overflow-y: auto !important; overflow-x: hidden !important;
    box-sizing: border-box !important; }}
/* Once the viewport is short (i.e. the user has zoomed in), a menu anchored to
   its card can still be pushed off the top or the bottom edge. Below this height
   it is centred like a modal instead, so it is always fully on screen. */
@media (max-height: 820px) {{
  html body div[data-testid="stPopoverBody"] {{
      top: 50% !important; left: 50% !important;
      right: auto !important; bottom: auto !important;
      transform: translate(-50%, -50%) !important;
      max-height: 86vh !important; }}
}}

/* Give width back to the page as the viewport shrinks, instead of squeezing the
   content off the right edge. The sidebar narrows but never disappears. */
@media (max-width: 1200px) {{
  section[data-testid="stSidebar"], div[data-testid="stSidebar"],
  [data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] {{
      width: 200px !important; min-width: 200px !important; max-width: 200px !important; }}
}}
@media (max-width: 900px) {{
  section[data-testid="stSidebar"], div[data-testid="stSidebar"],
  [data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] {{
      width: 164px !important; min-width: 164px !important; max-width: 164px !important; }}
  [data-testid="stSidebar"] .st-key-ui_logo_home .stButton > button p {{
      font-size: 19px !important; }}
}}
"""


def active_nav_css(key):
    """Highlight one of app.py's sidebar buttons as the current page."""
    return f"""
[data-testid="stSidebar"] .st-key-{key} .stButton > button {{
    background: {PRIMARY} !important; border-radius: 8px !important; }}
[data-testid="stSidebar"] .st-key-{key} .stButton > button p {{ color: #ECEDF4 !important; }}
[data-testid="stSidebar"] .st-key-{key} .stButton > button:hover {{
    background: {PRIMARY_MID} !important; }}
"""


def logo_home_button():
    """Append a clickable Cadence brand to app.py's sidebar (CSS floats it to the top).

    app.py stays untouched: its static `.sidebar-title` is hidden by SIDEBAR_CSS and this
    button takes its place, sending the user back to the dashboard.
    """
    with st.sidebar:
        if st.button("Cadence", key="ui_logo_home"):
            st.session_state.current_page = "dashboard"
            st.rerun()
