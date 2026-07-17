import streamlit as st

def dashboard():
    left, right = st.columns([1, 4])

    st.header("Dashboard")
    st.write("Welcome to your dashboard!")

    st.subheader("Your onboarding data (for now)")
    st.json(st.session_state.onboarding)