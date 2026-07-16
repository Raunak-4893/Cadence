from pages.onboarding import onboarding
from pages.dashboard import dashboard
from const import SUGGESTED_SUBJECTS
import json
import os
import re
import secrets
import smtplib
import sqlite3
import ssl
from contextlib import contextmanager
from datetime import date, datetime, timedelta, time
from email.message import EmailMessage
from typing import List, Tuple

import bcrypt
import streamlit as st
from dotenv import load_dotenv

st.set_page_config(layout="wide")

load_dotenv()
DB_PATH = "cadence.db"

if "page" not in st.session_state:
    st.session_state.page = 1

if "onboarding" not in st.session_state:
    st.session_state.onboarding = {
        "student_type": None,
        "goal": None,
        "routine": {
            "sleep_hours": 8,
            "school_hours": 6,
            "school_days": 5,
            "gym": False,
            "sports": False,
            "coaching": False,
            "commute": False,
            "part_time": False,
            "family": False,
            "extracurricular": False
        },
        "subjects": [],
    }

if "screen" not in st.session_state:
    st.session_state.screen = "onboarding"

hide_sidebar = st.session_state.screen == "onboarding"

st.markdown(f"""
<style>
{"[data-testid='stSidebar'] {display: none;}" if hide_sidebar else ""}
.block-container {{
    padding-top: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}}
</style>
""", unsafe_allow_html=True)

if st.session_state.screen == "onboarding":
    onboarding()

elif st.session_state.screen == "dashboard":
    dashboard()