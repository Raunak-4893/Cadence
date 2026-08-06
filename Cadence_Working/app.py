from pages.login import login
from pages.onboarding import onboarding
from pages.dashboard import dashboard
from pages.timetable import timetable
from pages.settings import settings
from const import SUGGESTED_SUBJECTS
import database as db
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
db.init_db()

if "page" not in st.session_state:
    st.session_state.page = 1

if "user" not in st.session_state:
    st.session_state.user = None

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
    st.session_state.screen = "login"

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

if st.session_state.screen in ("login", "onboarding"):
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .block-container { max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_custom_sidebar():
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

        if st.button("📊  Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()

        if st.button("🗓️  Timetable", use_container_width=True, key="nav_timetable"):
            st.session_state.current_page = "timetable"
            st.rerun()

        if st.button("⚙️  Settings", use_container_width=True, key="nav_settings"):
            st.session_state.current_page = "settings"
            st.rerun()

        st.divider()

        if st.button("🚪  Log out", use_container_width=True, key="nav_logout"):
            st.query_params.clear()          # drop any "Remember me" token
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.screen = "login"
            st.rerun()


if st.session_state.screen == "login":
    login()

elif st.session_state.screen == "onboarding":
    onboarding()

else:
    render_custom_sidebar()

    if st.session_state.current_page == "dashboard":
        dashboard()
    elif st.session_state.current_page == "timetable":
        timetable()
    elif st.session_state.current_page == "settings":
        settings()
    else:
        dashboard()