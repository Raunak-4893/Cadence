import streamlit as st
from datetime import date, datetime, timedelta

def _init_dashboard_state():
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

def _next_saturday():
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7  # 5 = Saturday
    days_ahead = days_ahead if days_ahead != 0 else 7
    return today + timedelta(days=days_ahead)

@st.dialog("Create your first study task")
def add_task_dialog():
    st.caption("ONE MORE THING")

    name = st.text_input("Task", placeholder="e.g. Revise calculus — chapter 4")

    subjects = st.session_state.onboarding.get("subjects", [])
    subject = st.selectbox(
        "Subject",
        options=subjects if subjects else ["No subjects added yet"],
        index=None,
        placeholder="Select your subject"
    )

    st.write("Priority")
    priority = st.pills(
        "Priority",
        options=["Important", "Medium", "Low"],
        default="Medium",
        label_visibility="collapsed"
    )

    st.write("Estimated duration")
    duration_choice = st.pills(
        "Estimated duration",
        options=["15 minutes", "30 minutes", "45 minutes", "1 hour", "Custom"],
        default="30 minutes",
        label_visibility="collapsed"
    )

    custom_duration = None
    if duration_choice == "Custom":
        custom_duration = st.number_input("Custom duration (mins)", min_value=5, step=5, value=30)

    st.write("Start date")
    date_choice = st.pills(
        "Start date",
        options=["Today", "Tomorrow", "This Weekend", "Custom"],
        default="Today",
        label_visibility="collapsed"
    )

    custom_date = None
    if date_choice == "Custom":
        custom_date = st.date_input("Pick a date", value=date.today())

    if st.button("Add Task", use_container_width=True):
        if not name or not subject or subject == "No subjects added yet":
            st.warning("Please fill in the task name and subject.")
            return

        duration_map = {"15 minutes": 15, "30 minutes": 30, "45 minutes": 45, "1 hour": 60}
        duration = custom_duration if duration_choice == "Custom" else duration_map[duration_choice]

        if date_choice == "Today":
            start_date = date.today()
        elif date_choice == "Tomorrow":
            start_date = date.today() + timedelta(days=1)
        elif date_choice == "This Weekend":
            start_date = _next_saturday()
        else:
            start_date = custom_date

        st.session_state.tasks.append({
            "name": name,
            "subject": subject,
            "duration": duration,
            "priority": priority,
            "completed": False,
            "start_date": start_date
        })
        st.rerun()

def dashboard():
    _init_dashboard_state()
    tasks = st.session_state.tasks
    today = date.today()

    today_tasks = [t for t in tasks if t.get("start_date") == today]
    overdue_tasks = [t for t in tasks if t.get("start_date") and t["start_date"] < today and not t.get("completed")]
    weekend_tasks = [t for t in tasks if t.get("start_date") and t["start_date"].weekday() in (5, 6) and t["start_date"] >= today]

    # Sync any checkbox clicks into task data BEFORE computing stats,
    # since a rerun triggered by a checkbox click otherwise renders the
    # stats/progress section using the pre-click value.
    for i, task in enumerate(today_tasks):
        key = f"today_{i}"
        if key in st.session_state:
            task["completed"] = st.session_state[key]

    for i, task in enumerate(overdue_tasks):
        key = f"overdue_{i}"
        if key in st.session_state:
            task["completed"] = st.session_state[key]

    for i, task in enumerate(weekend_tasks):
        key = f"weekend_{i}"
        if key in st.session_state:
            task["completed"] = st.session_state[key]

    # Header
    header_col, button_col = st.columns([4, 1])

    with header_col:
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        st.caption(greeting.upper())
        st.title("One task at a time. You've got this.")
        st.write("Here's your space. Add tasks and your plan takes shape.")

    with button_col:
        st.write("")
        st.write("")
        if st.button("+ Add Task", use_container_width=True):
            add_task_dialog()

    st.divider()

    # Stats
    completed_today = sum(1 for t in today_tasks if t["completed"])
    remaining_today = len(today_tasks) - completed_today
    week_progress = int((completed_today / len(today_tasks)) * 100) if today_tasks else 0
    overdue_pct = int((len(overdue_tasks) / len(tasks)) * 100) if tasks else 0

    stat1, stat2, stat3, stat4 = st.columns(4)

    with stat1:
        st.metric("Completed Today", completed_today)
        st.caption(f"of {len(today_tasks)} tasks")

    with stat2:
        st.metric("Remaining", remaining_today)
        st.caption("tasks left today")

    with stat3:
        st.metric("Week Progress", f"{week_progress}%")
        st.caption("completion rate")

    with stat4:
        st.metric("Overdue", f"{overdue_pct}%")
        st.caption("expired tasks")

    st.divider()

    # Main content
    left, right = st.columns([2, 1])

    with left:
        st.subheader(f"Today's plan  •  {len(today_tasks)} tasks")

        if today_tasks:
            st.write("Daily Progress")
            st.progress(week_progress / 100)
            st.caption(f"{week_progress}%")

            for i, task in enumerate(today_tasks):
                st.checkbox(
                    f"{task['name']} — {task['duration']} mins • {task['subject']} • {task['priority']}",
                    value=task["completed"],
                    key=f"today_{i}"
                )
        else:
            st.caption("No tasks for today yet. Add one to get started.")

    with right:
        st.subheader("Overdue tasks")
        if overdue_tasks:
            if st.button("Discard all"):
                st.session_state.tasks = [t for t in tasks if t not in overdue_tasks]
                st.rerun()

            for i, task in enumerate(overdue_tasks):
                st.checkbox(
                    f"{task['name']} — {task['subject']} • {task['priority']}",
                    value=task["completed"],
                    key=f"overdue_{i}"
                )
        else:
            st.caption("Nothing overdue.")

        st.subheader("Weekend Grind!")
        if weekend_tasks:
            for i, task in enumerate(weekend_tasks):
                st.checkbox(
                    f"{task['name']} — {task['subject']}",
                    value=task["completed"],
                    key=f"weekend_{i}"
                )
        else:
            st.caption("No weekend tasks yet.")