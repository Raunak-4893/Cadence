"""Shared task logic for Cadence.

The dialog and the scheduler are the project's original logic, moved here so the
dashboard and the timetable can both use them. Behaviour is unchanged; only the
surrounding presentation differs.
"""

from datetime import timedelta

import streamlit as st

import database as db
import time_utils

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PRIORITY_ORDER = {"Important": 0, "High": 0, "Medium": 1, "Low": 2}
# How much each priority counts towards progress. A hard, long task should move
# the bar further than a short, low-priority one.
PRIORITY_WEIGHT = {"Important": 3.0, "High": 3.0, "Medium": 2.0, "Low": 1.0}

COMMITMENT_HOURS = {
    "gym": 5, "sports": 5, "coaching": 8, "commute": 7,
    "part_time": 20, "family": 5, "extracurricular": 5,
}


def init_tasks():
    """Load this user's tasks into session state (original dashboard behaviour)."""
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if st.session_state.get("user") and not st.session_state.tasks:
        st.session_state.tasks = db.get_tasks(st.session_state.user[0])
    for task in st.session_state.tasks:
        if "deadline" not in task or task["deadline"] is None:
            task["deadline"] = (task.get("start_date") or time_utils.get_today()) + timedelta(days=7)
        if "is_weekend" not in task:
            task["is_weekend"] = False
    return st.session_state.tasks


def task_weight(task):
    """Effort-weighted value of a task: longer + higher priority counts for more."""
    minutes = max(5, int(task.get("duration") or 0))
    return (minutes / 30.0) * PRIORITY_WEIGHT.get(task.get("priority"), 2.0)


def weighted_progress(tasks):
    """Percentage of planned effort completed, weighted by duration and priority."""
    total = sum(task_weight(t) for t in tasks)
    if not total:
        return 0
    done = sum(task_weight(t) for t in tasks if t.get("completed"))
    return int(round(done / total * 100))


def daily_capacity_minutes():
    routine = st.session_state.onboarding.get("routine", {})
    sleep = routine.get("sleep_hours", 8) * 7
    school = routine.get("school_hours", 6) * routine.get("school_days", 5)
    commitments = sum(hrs for key, hrs in COMMITMENT_HOURS.items() if routine.get(key))
    free_hours_per_week = max(0, 168 - sleep - school - commitments)
    return (free_hours_per_week / 7) * 60


def weekend_enabled():
    return bool(st.session_state.onboarding.get("routine", {}).get("weekend_enabled", True))


def auto_schedule():
    """Spread pending tasks across the week by priority, duration and capacity.

    Weekend Grind Mode (`routine["weekend_enabled"]`): when ON, Saturday and
    Sunday are candidate days like any other, so spare weekend capacity soaks up
    the overflow. When OFF, only tasks explicitly marked "This Weekend" may land
    on Sat/Sun — everything else is kept to weekdays.
    """
    tasks = st.session_state.get("tasks", [])
    capacity_min = daily_capacity_minutes()
    allow_weekend = weekend_enabled()

    schedule = {day: [] for day in DAY_NAMES}
    remaining = {day: capacity_min for day in DAY_NAMES}

    pending = [t for t in tasks if not t.get("completed")]
    pending.sort(key=lambda t: (PRIORITY_ORDER.get(t["priority"], 1), t["duration"]))

    for task in pending:
        start_date = task.get("start_date")
        is_weekend = task.get("is_weekend", False)

        if is_weekend:
            # Explicit "This Weekend" tasks only go on Saturday or Sunday
            allowed_days = DAY_NAMES[5:7]
        elif allow_weekend:
            # Weekend Grind Mode on: any day is fair game
            allowed_days = list(DAY_NAMES)
        else:
            # Weekend Grind Mode off: keep the week's work on weekdays
            allowed_days = DAY_NAMES[0:5]

        fitting_days = [d for d in allowed_days if remaining[d] >= task["duration"]]

        if fitting_days:
            if not is_weekend and start_date:
                start_day_name = DAY_NAMES[start_date.weekday()]
                if start_day_name in fitting_days:
                    day = start_day_name
                else:
                    day = max(fitting_days, key=lambda d: remaining[d])
            else:
                day = max(fitting_days, key=lambda d: remaining[d])
        else:
            day = max(allowed_days, key=lambda d: remaining[d])

        schedule[day].append(task["id"])
        remaining[day] -= task["duration"]

    st.session_state.schedule = schedule
    st.session_state.scheduled_task_ids = {t["id"] for t in pending}


def ensure_schedule():
    """(Re)build the schedule whenever the set of pending tasks changed."""
    if "schedule" not in st.session_state:
        st.session_state.schedule = {day: [] for day in DAY_NAMES}
    if "scheduled_task_ids" not in st.session_state:
        st.session_state.scheduled_task_ids = set()
    pending_ids = {t["id"] for t in st.session_state.get("tasks", [])
                   if not t.get("completed")}
    if pending_ids != st.session_state.scheduled_task_ids:
        auto_schedule()


@st.dialog("Create your study task")
def add_task_dialog():
    """The project's original Add Task dialog, unchanged in behaviour."""
    st.caption("ONE MORE THING")

    name = st.text_input("Task", placeholder="e.g. Revise calculus — chapter 4",
                         key="tk_name")

    subjects = st.session_state.onboarding.get("subjects", [])
    subject = st.selectbox(
        "Subject",
        options=subjects if subjects else ["No subjects added yet"],
        index=None,
        placeholder="Select your subject",
        key="tk_subject",
    )

    st.write("Priority")
    priority = st.pills("Priority", options=["Important", "Medium", "Low"],
                        default="Medium", label_visibility="collapsed", key="tk_priority")

    st.write("Estimated duration")
    duration_choice = st.pills(
        "Estimated duration",
        options=["15 minutes", "30 minutes", "45 minutes", "1 hour", "Custom"],
        default="30 minutes", label_visibility="collapsed", key="tk_duration")

    custom_duration = None
    if duration_choice == "Custom":
        custom_duration = st.number_input("Custom duration (mins)", min_value=5, step=5,
                                          value=30, key="tk_custom_duration")

    st.write("Start date")
    date_choice = st.pills(
        "Start date", options=["Today", "Tomorrow", "This Weekend", "Custom"],
        default="Today", label_visibility="collapsed", key="tk_date")

    custom_date = None
    if date_choice == "Custom":
        custom_date = st.date_input("Pick a date", value=time_utils.get_today(),
                                    key="tk_custom_date")

    st.write("Deadline")
    st.caption("When does this task need to be done by? "
               "The scheduler prioritizes closer deadlines first.")
    deadline = st.date_input("Deadline",
                             value=time_utils.get_today() + timedelta(days=7),
                             min_value=time_utils.get_today(),
                             label_visibility="collapsed", key="tk_deadline")

    if st.button("Add Task", use_container_width=True, key="tk_submit"):
        if not name or not subject or subject == "No subjects added yet":
            st.warning("Please fill in the task name and subject.")
            return

        duration_map = {"15 minutes": 15, "30 minutes": 30, "45 minutes": 45, "1 hour": 60}
        duration = custom_duration if duration_choice == "Custom" else duration_map[duration_choice]

        if date_choice == "Today":
            start_date = time_utils.get_today()
        elif date_choice == "Tomorrow":
            start_date = time_utils.get_tomorrow()
        elif date_choice == "This Weekend":
            start_date = time_utils.get_next_saturday()
        else:
            start_date = custom_date

        if deadline < start_date:
            st.warning("Deadline can't be before the start date.")
            return

        new_task = {
            "name": name,
            "subject": subject,
            "duration": duration,
            "priority": priority,
            "completed": False,
            "start_date": start_date,
            "deadline": deadline,
            "is_weekend": date_choice == "This Weekend",
        }

        new_task["id"] = db.create_task(st.session_state.user[0], new_task)
        st.session_state.tasks.append(new_task)
        auto_schedule()
        st.rerun()
