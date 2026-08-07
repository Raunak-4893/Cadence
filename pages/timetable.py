"""Cadence — weekly timetable.

Scheduling logic is the project's original `_auto_schedule`; only the presentation
comes from the `Calender view` section of Study_Planner.fig. Every day is a real
Streamlit column and every task card is a real widget, so the menu and the visuals
are the same element (no separate drag board).
"""

import html
import re
from datetime import date, timedelta

import streamlit as st

import database as db
import time_utils
from const import SUGGESTED_SUBJECTS
from pages._tasks import check_week_rollover, is_carried_over
from pages._tasks import delete_task as _remove_task_everywhere
from pages._ui import (BASE_CSS, FAINT, GROTESK, INK, LINE, MUTED, PRIMARY,
                       RESPONSIVE_CSS, SANS, SERIF, SIDEBAR_CSS, active_nav_css,
                       logo_home_button, logo_svg)

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHORT_DAY = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
PRIORITY_ORDER = {"Important": 0, "High": 0, "Medium": 1, "Low": 2}

COMMITMENT_HOURS = {
    "gym": 5,
    "sports": 5,
    "coaching": 8,
    "commute": 7,
    "part_time": 20,
    "family": 5,
    "extracurricular": 5,
}

# ---- palette from the Figma frame ----
CANVAS_TT = "#F8F8FF"
CARD_BD = "#DFDFEE"
TRACK = "#E4E4EE"
FILL = "#8880C8"
BAR_BG = "#F0F0F8"
BAR_FG = "#ADADD3"
WARN_BG = "#FFF4ED"
WARN_BD = "#FDE8D4"
WARN_TX = "#92400E"
WARN_BTN = "#EA580C"
LATE = "#DC2626"
LATE_BG = "#FEF2F2"
LATE_BD = "#FCA5A5"
LATE_TX = "#B91C1C"
PRIORITY_COLOUR = {"High": "#EF4444", "Important": "#EF4444",
                   "Medium": "#F97316", "Low": "#9CA3AF"}
SUBJECT_COLOURS = ["#8385EA", "#B391ED", "#059669", "#0EA5E9", "#D946A6",
                   "#CA8A04", "#0891B2"]

CSS = f"""
<style>
{BASE_CSS}
[data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
    background: {CANVAS_TT} !important; }}
{SIDEBAR_CSS}
{active_nav_css("nav_timetable")}
[data-testid="stMainBlockContainer"] {{
    padding: 0 0 32px 0 !important; max-width: none !important; }}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
    max-width: none !important; }}

/* ---------------- top bar ---------------- */
.cad-top {{
    min-height: 56px; background: #FFFFFF; border-bottom: 1px solid {LINE};
    display: flex; align-items: center; flex-wrap: wrap; gap: 4px 0;
    padding: 8px 24px 8px 20px; box-sizing: border-box; }}
.cad-top .brand {{ display: flex; align-items: center; gap: 8px; }}
.cad-top .brand span {{
    font-family: {SERIF}; font-weight: 600; font-size: 15px; line-height: 22.5px;
    color: {PRIMARY}; }}
.cad-top .sep {{ width: 1px; height: 24px; background: {LINE}; margin: 0 20px; }}
.cad-top .title {{
    font-family: {SANS}; font-weight: 600; font-size: 16px; line-height: 24px;
    color: {INK}; }}
.cad-top .legend {{ margin-left: auto; display: flex; align-items: center; gap: 20px; }}
.cad-top .legend .i {{
    display: flex; align-items: center; gap: 6px; font-family: {GROTESK};
    font-weight: 400; font-size: 13px; line-height: 20px; color: {MUTED}; }}
.cad-top .legend .d {{ width: 8px; height: 8px; border-radius: 4px; }}
.cad-top .legend .box {{
    width: 12px; height: 12px; border: 1px solid {FAINT}; border-radius: 3px; }}
.cad-sub {{
    padding: 10px 20px 0 20px; font-family: {GROTESK}; font-weight: 400;
    font-size: 13px; line-height: 20px; color: {MUTED}; }}

/* rebuild button, styled as the Figma pill */
.st-key-tt_rebuild_wrap {{ padding: 10px 20px 4px 20px !important; }}
[data-testid="stMain"] .st-key-tt_rebuild_wrap button {{
    width: auto !important; height: 32px !important; min-height: 32px !important;
    border-radius: 8px !important; background: #FFFFFF !important;
    border: 1px solid {LINE} !important; padding: 0 14px !important;
    box-shadow: none !important; }}
[data-testid="stMain"] .st-key-tt_rebuild_wrap button p {{
    font-family: {GROTESK} !important; font-weight: 500 !important;
    font-size: 13px !important; color: {INK} !important; }}

/* ---------------- capacity banner ---------------- */
.cad-warn {{
    margin: 8px 20px 0 20px; min-height: 48px; background: {WARN_BG};
    border: 1px solid {WARN_BD}; border-radius: 10px; display: flex;
    align-items: center; gap: 10px; padding: 7px 16px; box-sizing: border-box; }}
.cad-warn .ic {{ font-size: 18px; line-height: 27px; }}
.cad-warn .tx {{
    font-family: {GROTESK}; font-weight: 700; font-size: 13px; line-height: 19.5px;
    color: {WARN_TX}; }}

/* ---------------- week grid ---------------- */
.st-key-tt_grid {{ padding: 12px 20px 0 20px !important; gap: 0 !important; }}
.st-key-tt_grid [data-testid="stHorizontalBlock"] {{
    flex-wrap: nowrap !important; overflow-x: auto !important;
    padding-bottom: 6px !important; }}
.st-key-tt_grid [data-testid="stColumn"] {{
    background: #FFFFFF; border: 1px solid {LINE}; border-right: none;
    min-height: 520px; min-width: 146px !important; padding: 0 !important; }}
.st-key-tt_grid [data-testid="stColumn"]:last-child {{
    border-right: 1px solid {LINE}; border-radius: 0 10px 10px 0; }}
.st-key-tt_grid [data-testid="stColumn"]:first-child {{ border-radius: 10px 0 0 10px; }}
.st-key-tt_grid [data-testid="stColumn"] > div {{ padding: 0 8px 8px 8px; }}
.cad-dayhd {{
    padding: 10px 4px 8px 4px; border-bottom: 1px solid {LINE}; margin: 0 -8px 8px -8px;
    padding-left: 12px; padding-right: 12px; }}
.cad-dayhd .r1 {{ display: flex; align-items: center; gap: 8px; }}
.cad-dayhd .dw {{
    font-family: {GROTESK}; font-weight: 700; font-size: 12px; line-height: 18px;
    color: {FAINT}; }}
.cad-dayhd .dd {{
    font-family: {GROTESK}; font-weight: 700; font-size: 15px; line-height: 22.5px;
    color: {INK}; }}
.cad-dayhd .track {{
    margin-top: 6px; height: 4px; border-radius: 3px; background: {TRACK};
    overflow: hidden; }}
.cad-dayhd .track i {{
    display: block; height: 4px; border-radius: 3px; background: {FILL}; }}
.cad-dayhd .track i.over {{ background: {WARN_BTN}; }}
.cad-dayhd .r2 {{
    margin-top: 5px; display: flex; justify-content: space-between; align-items: center; }}
.cad-dayhd .r2 span {{
    font-family: {GROTESK}; font-weight: 400; font-size: 11px; line-height: 16.5px;
    color: {MUTED}; }}
.cad-dayempty {{
    padding: 18px 0; text-align: center; font-family: {GROTESK}; font-weight: 400;
    font-size: 11px; line-height: 16.5px; color: {FAINT}; }}

/* ---------------- task card = a popover trigger wearing the Figma card ---- */
[class*="st-key-tt_card_"] {{ position: relative !important; margin-bottom: 8px !important; }}
[class*="st-key-tt_card_"] [data-testid="stPopover"] {{
    position: absolute !important; inset: 0 !important; z-index: 3 !important; }}
[class*="st-key-tt_card_"] [data-testid="stPopover"] > div {{ height: 100% !important; }}
[data-testid="stMain"] [class*="st-key-tt_card_"] [data-testid="stPopover"] button {{
    width: 100% !important; height: 100% !important; min-height: 100% !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important; opacity: 0 !important;
    cursor: pointer !important; }}
.cad-tc {{
    background: #FFFFFF; border: 1px solid {CARD_BD}; border-radius: 8px;
    padding: 8px 10px; box-sizing: border-box; }}
.cad-tc:hover {{ border-color: {PRIMARY}; }}
.cad-tc .r1 {{ display: flex; justify-content: space-between; align-items: center; }}
.cad-tc .sub {{
    font-family: {GROTESK}; font-weight: 700; font-size: 10px; line-height: 15px;
    letter-spacing: .02em; }}
.cad-tc .pri {{ display: flex; align-items: center; gap: 4px; }}
.cad-tc .pri i {{ width: 6px; height: 6px; border-radius: 3px; display: block; }}
.cad-tc .pri span {{
    font-family: {SANS}; font-weight: 500; font-size: 10px; line-height: 15px; }}
.cad-tc .nm {{
    padding-top: 4px; font-family: {GROTESK}; font-weight: 600; font-size: 13px;
    line-height: 16.9px; color: {INK}; }}
.cad-tc.done .nm {{ color: {FAINT}; text-decoration: line-through; }}
.cad-tc.done {{ background: #FBFBFE; }}
/* carried over from a week that already ended */
.cad-tc.late {{ background: {LATE_BG}; border-color: {LATE_BD}; }}
.cad-tc.late:hover {{ border-color: {LATE}; }}
.cad-tc.late .nm {{ color: {LATE_TX}; }}
.cad-tc.late .track {{ background: #FBD5D5; }}
.cad-tc.late .track i {{ background: {LATE}; }}
.cad-tc .r2 .late {{
    font-family: {GROTESK}; font-weight: 700; font-size: 10px; line-height: 15px;
    letter-spacing: .02em; color: {LATE}; }}
.cad-tc .track {{
    margin-top: 6px; height: 3px; border-radius: 2px; background: {BAR_BG};
    overflow: hidden; }}
.cad-tc .track i {{
    display: block; height: 3px; border-radius: 2px; background: {BAR_FG}; }}
.cad-tc .r2 {{
    padding-top: 6px; display: flex; justify-content: space-between; align-items: center; }}
.cad-tc .r2 .t {{
    font-family: {GROTESK}; font-weight: 400; font-size: 11px; line-height: 16.5px;
    color: {FAINT}; }}
.cad-tc .r2 .done {{
    font-family: {GROTESK}; font-weight: 700; font-size: 10px; line-height: 15px;
    color: #00A63E; }}

/* ---------------- the task menu ---------------- */
[data-testid="stPopoverBody"] {{ min-width: 320px !important; }}
[data-testid="stPopoverBody"] [data-testid="stRadio"] label p {{
    font-family: {GROTESK} !important; font-size: 13px !important;
    color: {INK} !important; }}
[data-testid="stPopoverBody"] [data-testid="stRadio"] > div {{
    max-height: 132px; overflow-y: auto; gap: 2px !important; }}
[data-testid="stPopoverBody"] [data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 4px !important; }}
[data-testid="stPopoverBody"] [data-testid="stTabs"] button[data-baseweb="tab"] p {{
    font-family: {GROTESK} !important; font-size: 13px !important;
    font-weight: 600 !important; }}
html body [class*="st-key-tt_delwrap_"] button {{
    background: #DC2626 !important; border: 1px solid #DC2626 !important;
    box-shadow: none !important; }}
html body [class*="st-key-tt_delwrap_"] button p {{
    color: #FFFFFF !important; font-weight: 600 !important; }}
[data-testid="stPopoverBody"] h4 {{
    font-family: {GROTESK} !important; font-size: 13px !important;
    font-weight: 700 !important; color: {INK} !important; margin: 0 0 4px 0 !important; }}
/* ---------------- zoom / narrow viewports ---------------- */
@media (max-width: 1000px) {{
  .cad-top .legend {{ display: none !important; }}
}}
@media (max-width: 700px) {{
  .cad-top .title {{ font-size: 14px !important; }}
  .cad-sub {{ font-size: 12px !important; }}
}}
{RESPONSIVE_CSS}
</style>
"""


# --------------------------------------------------------------------------
# original scheduling logic — unchanged
# --------------------------------------------------------------------------

def _daily_capacity_minutes():
    routine = st.session_state.onboarding.get("routine", {})
    sleep = routine.get("sleep_hours", 8) * 7
    school = routine.get("school_hours", 6) * routine.get("school_days", 5)
    commitments = sum(hrs for key, hrs in COMMITMENT_HOURS.items() if routine.get(key))
    free_hours_per_week = max(0, 168 - sleep - school - commitments)
    return (free_hours_per_week / 7) * 60


def _init_schedule_state():
    if "schedule" not in st.session_state:
        st.session_state.schedule = {day: [] for day in DAY_NAMES}
    if "scheduled_task_ids" not in st.session_state:
        st.session_state.scheduled_task_ids = set()


def _auto_schedule():
    tasks = st.session_state.get("tasks", [])
    capacity_min = _daily_capacity_minutes()

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
        else:
            # Today/Tomorrow/Custom tasks can go on any day, but prefer start_date's day
            allowed_days = list(DAY_NAMES)

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


# --------------------------------------------------------------------------
# "Regenerate schedule" — rebalance instead of rebuilding the same board
# --------------------------------------------------------------------------

def _deadline_limit(task, today):
    """Last weekday index (0=Mon) this task may sit on, given its deadline.

    A task due on Wednesday should never be parked on Saturday just because
    Saturday happens to be the emptiest day. A task due beyond this week — or one
    that is already overdue, where the deadline tells us nothing useful any more —
    is free to go anywhere in the week.
    """
    deadline = task.get("deadline")
    if not deadline:
        return 6
    week_start = today - timedelta(days=today.weekday())
    offset = (deadline - week_start).days
    if offset > 6 or offset < today.weekday():
        return 6
    return offset


def _allowed_days(task, today):
    """Every day this task is legally allowed to sit on."""
    allowed = DAY_NAMES[5:7] if task.get("is_weekend") else list(DAY_NAMES)
    limit = _deadline_limit(task, today)
    return [d for d in allowed if DAY_NAMES.index(d) <= limit] or allowed


def _spread_cost(load):
    """Lower is a flatter week: cut the worst day first, then even out the rest."""
    return (max(load.values()), sum(v * v for v in load.values()))


def _rebalance_schedule():
    """Reshuffle the WHOLE week: every task leaves the day it is on and the load
    is levelled across the seven days.

    `_auto_schedule` is anchored to each task's start date, so re-running it just
    rebuilds the identical board. This does three things instead:

      1. every task — completed ones included — is barred from the day it is
         currently on, so the board genuinely changes on every press;
      2. the biggest, most urgent sessions are placed first onto whichever day
         ends up lightest, so nothing piles onto one day;
      3. a set of improvement sweeps then relocates individual tasks for as long
         as that keeps flattening the week.

    The only fixed rules are the ones the schedule has always had: "This Weekend"
    tasks stay on Saturday/Sunday, and nothing lands after its deadline.
    """
    tasks = st.session_state.get("tasks", [])
    if not tasks:
        return 0, 0.0

    capacity = _daily_capacity_minutes()
    today = date.today()
    by_id = {t["id"]: t for t in tasks}

    previous = {tid: day for day, ids in st.session_state.schedule.items()
                for tid in ids if tid in by_id}
    for task in tasks:
        previous.setdefault(
            task["id"],
            DAY_NAMES[(task.get("start_date") or today).weekday()])

    # Big rocks first: the longest, highest-priority sessions get the pick of the
    # week and the short ones fill the gaps. Packs far flatter than shortest-first.
    order = sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t["priority"], 1),
                                         -t["duration"]))

    # Days within this much of each other count as equally good, which gives the
    # shuffle room to move things without unbalancing the week.
    tolerance = max(15.0, capacity * 0.10)
    spin = st.session_state.get("tt_rebuild_spin", 0)

    schedule = {day: [] for day in DAY_NAMES}
    load = {day: 0.0 for day in DAY_NAMES}
    options = {}

    for n, task in enumerate(order):
        allowed = _allowed_days(task, today)
        options[task["id"]] = allowed
        # Everything moves: the current day is taken off the table unless it is
        # the only day this task is allowed on at all.
        candidates = [d for d in allowed if d != previous.get(task["id"])] or allowed
        # Rotate the sweep so equally-good days aren't always resolved
        # Monday-first; each press starts somewhere else.
        offset = (spin + n) % len(candidates)
        candidates = candidates[offset:] + candidates[:offset]

        day = min(candidates,
                  key=lambda d, dur=task["duration"]: (int((load[d] + dur) // tolerance),
                                                       load[d] + dur))
        schedule[day].append(task["id"])
        load[day] += task["duration"]

    def can_sit(tid, day):
        """A task may take a day if it is legal for it and isn't where it started."""
        return day in options[tid] and day != previous.get(tid)

    def relocate_once():
        """Move a single task to a lighter day, if that flattens the week."""
        for source in DAY_NAMES:
            for tid in list(schedule[source]):
                duration = by_id[tid]["duration"]
                for target in options[tid]:
                    if target == source or not can_sit(tid, target):
                        continue
                    before = _spread_cost(load)
                    load[source] -= duration
                    load[target] += duration
                    if _spread_cost(load) < before:
                        schedule[source].remove(tid)
                        schedule[target].append(tid)
                        return True
                    load[source] += duration
                    load[target] -= duration
        return False

    def swap_once():
        """Trade two tasks between days. Sometimes neither can move alone without
        going back where it came from, but the pair can trade and flatten the week."""
        for i, day_a in enumerate(DAY_NAMES):
            for day_b in DAY_NAMES[i + 1:]:
                for ta in list(schedule[day_a]):
                    for tb in list(schedule[day_b]):
                        if not can_sit(ta, day_b) or not can_sit(tb, day_a):
                            continue
                        delta = by_id[tb]["duration"] - by_id[ta]["duration"]
                        if not delta:
                            continue
                        before = _spread_cost(load)
                        load[day_a] += delta
                        load[day_b] -= delta
                        if _spread_cost(load) < before:
                            schedule[day_a].remove(ta)
                            schedule[day_b].remove(tb)
                            schedule[day_a].append(tb)
                            schedule[day_b].append(ta)
                            return True
                        load[day_a] -= delta
                        load[day_b] += delta
        return False

    # Improvement sweeps: keep relocating and trading tasks for as long as that
    # flattens the week. Nothing is ever allowed back onto the day it came from.
    for _ in range(40):
        if not (relocate_once() or swap_once()):
            break

    st.session_state.schedule = schedule
    st.session_state.scheduled_task_ids = {t["id"] for t in tasks
                                           if not t.get("completed")}
    st.session_state.tt_rebuild_spin = spin + 1

    landed = {tid: day for day, ids in schedule.items() for tid in ids}
    moved = sum(1 for tid, day in landed.items() if previous.get(tid) != day)
    return moved, max(load.values())


# --------------------------------------------------------------------------
# task menu (replaces drag and drop)
# --------------------------------------------------------------------------

def _day_of(task_id):
    for day, ids in st.session_state.schedule.items():
        if task_id in ids:
            return day
    return None


def _minutes_used(day, tasks_by_id):
    """Minutes already committed on a day."""
    return sum(tasks_by_id[tid]["duration"]
               for tid in st.session_state.schedule.get(day, [])
               if tid in tasks_by_id)


def _days_with_room(task, tasks_by_id):
    """Days this task fits on without exceeding that day's free time."""
    capacity = _daily_capacity_minutes()
    current = _day_of(task["id"])
    fits, full = [], []
    for day in DAY_NAMES:
        if day == current:
            continue
        free = capacity - _minutes_used(day, tasks_by_id)
        (fits if free >= task["duration"] else full).append((day, max(0, free)))
    return fits, full


def _move_task(task_id, target_day):
    for day in DAY_NAMES:
        if task_id in st.session_state.schedule.get(day, []):
            st.session_state.schedule[day].remove(task_id)
    st.session_state.schedule.setdefault(target_day, []).append(task_id)


def _delete_task(task_id):
    """Same delete the Dashboard's trash button uses, so the two can't drift."""
    _remove_task_everywhere(task_id)


def _subject_colour(name):
    if not name:
        return SUBJECT_COLOURS[0]
    return SUBJECT_COLOURS[sum(ord(c) for c in name) % len(SUBJECT_COLOURS)]


def _card_html(task):
    colour = _subject_colour(task.get("subject"))
    pri = task.get("priority") or "Medium"
    pcol = PRIORITY_COLOUR.get(pri, PRIORITY_COLOUR["Medium"])
    done = bool(task.get("completed"))
    late = is_carried_over(task) and not done
    mins = int(task.get("duration") or 0)
    dur = f"{mins} min" if mins < 60 else (f"{mins // 60}h" if mins % 60 == 0
                                           else f"{mins / 60:.1f}h")
    if done:
        right = '<span class="done">DONE</span>'
    elif late:
        right = '<span class="late">FROM LAST WEEK</span>'
    else:
        right = '<span></span>'
    classes = "cad-tc" + (" done" if done else "") + (" late" if late else "")
    return (f'<div class="{classes}">'
            f'<div class="r1"><span class="sub" style="color:{colour}">'
            f'{html.escape((task.get("subject") or "GENERAL").upper())}</span>'
            f'<span class="pri"><i style="background:{pcol}"></i>'
            f'<span style="color:{pcol}">{html.escape(pri)}</span></span></div>'
            f'<div class="nm">{html.escape(task["name"])}</div>'
            f'<div class="track"><i style="width:{100 if done else 0}%"></i></div>'
            f'<div class="r2">{right}<span class="t">{dur}</span></div></div>')


def _task_card(task, tasks_by_id):
    """The Figma card, with the whole card acting as the menu trigger."""
    tid = task["id"]
    with st.container(key=f"tt_card_{tid}"):
        st.markdown(_card_html(task), unsafe_allow_html=True)
        with st.popover("Options", use_container_width=True):
            st.markdown(f"#### {html.escape(task['name'])}")
            st.caption(f"{task['subject']} • {task['priority']} • {task['duration']} min"
                       + (" • completed" if task.get("completed") else ""))

            # Tabs, not one long stack: the old menu was ~990px tall, so at any
            # zoom above 60% "Move task" and "Remove task" fell off the bottom of
            # the screen. Only one section is on screen at a time now.
            tab_edit, tab_move, tab_del = st.tabs(["Edit", "Move", "Delete"])

            with tab_edit:
                new_name = st.text_input("Task name", value=task["name"],
                                         key=f"tt_name_{tid}")
                subjects = list(st.session_state.onboarding.get("subjects", []))
                if not subjects:
                    subjects = list(SUGGESTED_SUBJECTS)
                if task["subject"] and task["subject"] not in subjects:
                    subjects.insert(0, task["subject"])
                idx = subjects.index(task["subject"]) if task["subject"] in subjects else 0
                new_subject = st.selectbox("Subject", subjects, index=idx,
                                           key=f"tt_subject_{tid}")
                st.caption("Name and subject only — to change duration, priority or "
                           "dates, delete this task and add a new one.")
                if st.button("Save changes", key=f"tt_save_{tid}",
                             use_container_width=True):
                    if not new_name.strip():
                        st.warning("Task name can't be empty.")
                    else:
                        task["name"] = new_name.strip()
                        task["subject"] = new_subject
                        db.update_task(task)
                        st.rerun()

            with tab_move:
                fits, full = _days_with_room(task, tasks_by_id)
                if not fits:
                    st.caption("No other day has enough free time left for this task.")
                else:
                    free_by_day = dict(fits)
                    # A radio list, not a selectbox: the day must be picked from the
                    # visible options rather than typed in.
                    choice = st.radio(
                        "Day", [d for d, _ in fits],
                        format_func=lambda d: f"{d} — {free_by_day[d] / 60:.1f}h free",
                        key=f"tt_move_{tid}", label_visibility="collapsed")
                    if st.button("Move task", key=f"tt_movebtn_{tid}",
                                 use_container_width=True):
                        _move_task(tid, choice)
                        st.rerun()
                if full:
                    st.caption("Not enough room on: "
                               + ", ".join(f"{d} ({f / 60:.1f}h)" for d, f in full))

            with tab_del:
                st.caption("This removes the task from the timetable and the "
                           "dashboard. It can't be undone.")
                with st.container(key=f"tt_delwrap_{tid}"):
                    if st.button("🗑️ Remove task", key=f"tt_del_{tid}",
                                 use_container_width=True):
                        _delete_task(tid)
                        st.rerun()


# --------------------------------------------------------------------------

def timetable():
    st.markdown(CSS, unsafe_allow_html=True)
    logo_home_button()

    user_id = st.session_state.user[0]

    # Tasks are created on the Dashboard; the timetable reads the same list.
    if "tasks" not in st.session_state or not st.session_state.tasks:
        st.session_state.tasks = db.get_tasks(user_id)

    # A new week wipes the board; anything unfinished is the user's call.
    check_week_rollover()

    _init_schedule_state()
    tasks = st.session_state.get("tasks", [])
    tasks_by_id = {t["id"]: t for t in tasks}

    legend = ('<div class="legend">'
              '<div class="i"><span class="d" style="background:#6366F1"></span>'
              'Study block</div>'
              '<div class="i"><span class="d" style="background:#4CAF72"></span>'
              'Completed</div>'
              '<div class="i"><span class="box"></span>Free</div></div>')
    st.markdown(
        f'<div class="cad-top"><div class="brand">{logo_svg(PRIMARY, 27.75, 30)}'
        f'<span>Cadence</span></div><div class="sep"></div>'
        f'<div class="title">Study Timetable</div>{legend}</div>',
        unsafe_allow_html=True)
    st.markdown('<div class="cad-sub">Tasks are spread across your week by priority '
                'and duration. Click a task to edit it, move it to another day, or '
                'remove it. Add new tasks from the Dashboard.</div>',
                unsafe_allow_html=True)

    if not tasks:
        st.info("No tasks yet — add some from the Dashboard and they'll show up here.")
        return

    # Anything added or completed on the Dashboard lands here automatically.
    pending_ids = {t["id"] for t in tasks if not t.get("completed")}
    if pending_ids - st.session_state.scheduled_task_ids:
        _auto_schedule()
    st.session_state.scheduled_task_ids = pending_ids

    # Ticking a task off on the Dashboard must cross it out here, not make it vanish,
    # so any completed task missing from the board is pinned back onto its own day.
    placed = {tid for ids in st.session_state.schedule.values() for tid in ids}
    for t in tasks:
        if t.get("completed") and t["id"] not in placed:
            when = t.get("start_date") or date.today()
            st.session_state.schedule.setdefault(DAY_NAMES[when.weekday()], []).append(t["id"])

    with st.container(key="tt_rebuild_wrap"):
        if st.button("🔄 Regenerate schedule", key="tt_regenerate",
                     help="Reshuffles the whole week: every task moves to a new "
                          "day, chosen so the load is spread evenly and nothing "
                          "lands after its deadline."):
            moved, busiest = _rebalance_schedule()
            st.session_state.tt_rebuild_note = (moved, len(tasks), busiest)
            st.rerun()

    note = st.session_state.pop("tt_rebuild_note", None)
    if note:
        moved, total, busiest = note
        st.toast(f"Week reshuffled — {moved} of {total} tasks moved to a new day. "
                 f"Busiest day is now {busiest / 60:.1f}h.")

    capacity_min = _daily_capacity_minutes()

    over_days = []
    for day in DAY_NAMES:
        used = _minutes_used(day, tasks_by_id)
        if used > capacity_min + 1e-9:
            over_days.append((day, used))
    if over_days:
        day, used = over_days[0]
        st.markdown(
            f'<div class="cad-warn"><span class="ic">⚠️</span>'
            f'<span class="tx">{day} is over capacity. You have planned '
            f'{used / 60:.1f}h against about {capacity_min / 60:.1f}h of typical free '
            f'time. Move a session to a lighter day.</span></div>',
            unsafe_allow_html=True)

    with st.container(key="tt_grid"):
        cols = st.columns(7, gap="small")
        for i, day in enumerate(DAY_NAMES):
            with cols[i]:
                day_ids = [tid for tid in st.session_state.schedule.get(day, [])
                           if tid in tasks_by_id]
                day_tasks = [tasks_by_id[tid] for tid in day_ids]
                used = sum(t["duration"] for t in day_tasks)
                pct = min(100, round(used / capacity_min * 100)) if capacity_min else 0
                over = used > capacity_min + 1e-9
                st.markdown(
                    f'<div class="cad-dayhd"><div class="r1">'
                    f'<span class="dw">{SHORT_DAY[i]}</span></div>'
                    f'<div class="track"><i class="{"over" if over else ""}" '
                    f'style="width:{pct}%"></i></div>'
                    f'<div class="r2"><span>{used / 60:.1f} / '
                    f'{capacity_min / 60:.1f}h</span><span>{pct}%</span></div></div>',
                    unsafe_allow_html=True)

                for task in day_tasks:
                    _task_card(task, tasks_by_id)

                if not day_tasks:
                    st.markdown('<div class="cad-dayempty">Nothing planned</div>',
                                unsafe_allow_html=True)
