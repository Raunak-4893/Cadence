from pages.onboarding import onboarding
from pages.dashboard import dashboard
from pages.timetable import timetable
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

st.markdown("""
<style>
.block-container {
    padding-top: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
</style>
""", unsafe_allow_html=True)

def render_custom_sidebar(dashboard_page, timetable_page):
    with st.sidebar:
        st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        .sidebar-title {
            font-size: 1.4rem;
            font-weight: 700;
            padding: 0.5rem 0 1.5rem 0;
        }
        </style>
        <div class="sidebar-title">Cadence</div>
        """, unsafe_allow_html=True)

        if st.button("📊  Dashboard", use_container_width=True):
            st.switch_page(dashboard_page)

        if st.button("🗓️  Timetable", use_container_width=True):
            st.switch_page(timetable_page)

if st.session_state.screen == "onboarding":
    onboarding_page = st.Page(onboarding, title="Onboarding")
    nav = st.navigation([onboarding_page], position="hidden")

else:
    dashboard_page = st.Page(dashboard, title="Dashboard", url_path="dashboard")
    timetable_page = st.Page(timetable, title="Timetable", url_path="timetable")
    nav = st.navigation([dashboard_page, timetable_page], position="hidden")

    if st.session_state.pop("redirect_to_dashboard", False):
        st.switch_page(dashboard_page)

    render_custom_sidebar(dashboard_page, timetable_page)

nav.run()