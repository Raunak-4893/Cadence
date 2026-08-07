from datetime import date, time, timedelta
import random
from typing import Dict, List, Optional, Tuple

import database as db

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHORT_DAY = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

PRIORITY_RANK = {"Important": 0, "High": 0, "Medium": 1, "Low": 2}

SCHOOL_START_HOUR = 8
SLEEP_START_HOUR = 22
MINUTES_PER_DAY = 1440


def fmt_time(minutes: int) -> str:
    minutes = minutes % MINUTES_PER_DAY
    h = minutes // 60
    m = minutes % 60
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ampm}"


def _to_min_from_str(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def _merge(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(int(m[0]), int(m[1])) for m in merged]


def _subtract(base: List[Tuple[int, int]], cuts: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    base = _merge(base)
    cuts = _merge(cuts)
    if not cuts:
        return base
    result = []
    for bs, be in base:
        cur = bs
        for cs, ce in cuts:
            if ce <= cur or cs >= be:
                continue
            if cs > cur:
                result.append((cur, cs))
            cur = max(cur, ce)
            if cur >= be:
                break
        if cur < be:
            result.append((cur, be))
    return result


def free_windows_for_weekday(user_id: int, weekday: int, routine: dict) -> List[Tuple[int, int]]:
    sleep_hours = routine.get("sleep_hours", 8)
    school_hours = routine.get("school_hours", 6)
    school_days = routine.get("school_days", 5)

    unavailable = []

    sleep_start = SLEEP_START_HOUR * 60
    sleep_end = sleep_start + sleep_hours * 60
    if sleep_end <= MINUTES_PER_DAY:
        unavailable.append((sleep_start, sleep_end))
    else:
        unavailable.append((sleep_start, MINUTES_PER_DAY))
        unavailable.append((0, sleep_end % MINUTES_PER_DAY))

    if weekday < school_days:
        school_s = SCHOOL_START_HOUR * 60
        school_e = school_s + school_hours * 60
        unavailable.append((school_s, school_e))

    for slot in db.get_busy_slots(user_id):
        if slot["day_of_week"] == weekday:
            unavailable.append((
                _to_min_from_str(slot["start_time"]),
                _to_min_from_str(slot["end_time"]),
            ))

    return _subtract([(0, MINUTES_PER_DAY)], unavailable)


def get_routine(user_id: int) -> dict:
    profile = db.get_onboarding_profile(user_id)
    if not profile:
        return {
            "sleep_hours": 8,
            "school_hours": 6,
            "school_days": 5,
            "weekend_enabled": True,
        }
    return {
        "sleep_hours": profile.get("sleep_hours", 8),
        "school_hours": profile.get("school_hours", 6),
        "school_days": profile.get("school_days", 5),
        "weekend_enabled": bool(profile.get("weekend_enabled", True)),
    }


def _coerce_date(value):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except Exception:
            pass
    return None


def schedule_tasks(
    user_id: int,
    tasks: List[dict],
    allow_weekend: Optional[bool] = None,
    planning_days: int = 14,
    seed: Optional[int] = None,
) -> Tuple[Dict[str, List[int]], Dict[int, dict], List[int]]:
    routine = get_routine(user_id)
    if allow_weekend is None:
        allow_weekend = routine.get("weekend_enabled", True)

    today = date.today()
    horizon_end = today + timedelta(days=planning_days - 1)

    pending = [t for t in tasks if not t.get("completed")]
    if not pending:
        return {day: [] for day in DAY_NAMES}, {}, []

    rng = random.Random(seed)
    pending.sort(key=lambda t: (
        _coerce_date(t.get("deadline")) or (today + timedelta(days=7)),
        PRIORITY_RANK.get(t.get("priority", "Medium"), 1),
        rng.random(),
    ))

    scheduled_intervals: Dict[date, List[Tuple[int, int]]] = {}
    placements_by_date: Dict[date, List[dict]] = {}

    def free_on_date(d: date):
        windows = list(free_windows_for_weekday(user_id, d.weekday(), routine))
        cuts = scheduled_intervals.get(d, [])
        return _subtract(windows, cuts)

    def place(d: date, start: int, end: int, task_id: int):
        scheduled_intervals.setdefault(d, []).append((start, end))
        placements_by_date.setdefault(d, []).append({
            "task_id": task_id,
            "start_min": start,
            "end_min": end,
        })

    def load_on_date(d: date):
        return sum(pl["end_min"] - pl["start_min"] for pl in placements_by_date.get(d, []))

    unscheduled = []

    for task in pending:
        deadline = _coerce_date(task.get("deadline")) or (today + timedelta(days=7))
        start_date = _coerce_date(task.get("start_date")) or today
        start_date = max(today, start_date)
        duration = int(task.get("duration", 30))

        # Build all candidate days in the search window
        search_end = min(horizon_end, deadline + timedelta(days=7))

        candidate_days = []
        d = today
        while d <= search_end:
            candidate_days.append(d)
            d += timedelta(days=1)

        if not allow_weekend:
            candidate_days = [d for d in candidate_days if d.weekday() < 5]

        # Score: tasks cannot go before start_date, then prefer weekdays,
        # then least existing load (even spread), then start_date preference,
        # then earlier date, then random tiebreak.
        def day_score(d):
            if d < start_date:
                return (1, 0, 0, 0, 0, 0)  # disqualified
            is_weekday = 0 if d.weekday() < 5 else 1
            is_preferred = 0 if d == start_date else 1
            load = load_on_date(d)
            return (0, is_weekday, load, is_preferred, d.toordinal(), rng.random())

        candidate_days.sort(key=day_score)

        placed = False
        for d in candidate_days:
            windows = free_on_date(d)
            for w_start, w_end in windows:
                if w_end - w_start >= duration:
                    place(d, w_start, w_start + duration, task["id"])
                    placed = True
                    break
            if placed:
                break

        if not placed:
            unscheduled.append(task["id"])

    schedule_map = {day: [] for day in DAY_NAMES}
    time_map = {}
    for d, placements in placements_by_date.items():
        day_name = DAY_NAMES[d.weekday()]
        for pl in placements:
            schedule_map[day_name].append(pl["task_id"])
            time_map[pl["task_id"]] = {
                "date": d,
                "start_min": pl["start_min"],
                "end_min": pl["end_min"],
            }

    return schedule_map, time_map, unscheduled


def assign_times_for_week(
    user_id: int,
    schedule_map: Dict[str, List[int]],
    week_start: date,
    tasks_by_id: Dict[int, dict],
) -> Dict[int, dict]:
    routine = get_routine(user_id)

    scheduled_intervals: Dict[date, List[Tuple[int, int]]] = {}
    time_map = {}

    for i, day_name in enumerate(DAY_NAMES):
        task_ids = schedule_map.get(day_name, [])
        if not task_ids:
            continue

        d = week_start + timedelta(days=i)
        weekday = d.weekday()
        windows = list(free_windows_for_weekday(user_id, weekday, routine))
        cuts = scheduled_intervals.get(d, [])
        windows = _subtract(windows, cuts)

        for tid in task_ids:
            task = tasks_by_id.get(tid)
            if not task:
                continue
            duration = int(task.get("duration", 30))

            placed = False
            for idx, (w_start, w_end) in enumerate(windows):
                if w_end - w_start >= duration:
                    start = w_start
                    end = start + duration
                    time_map[tid] = {"date": d, "start_min": start, "end_min": end}
                    scheduled_intervals.setdefault(d, []).append((start, end))
                    if end < w_end:
                        windows[idx] = (end, w_end)
                    else:
                        windows.pop(idx)
                    placed = True
                    break
            if not placed:
                pass

    return time_map