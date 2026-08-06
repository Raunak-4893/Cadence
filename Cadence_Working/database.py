# database.py
# --------------------------------------------------------------------------
# SQLite backend for users, onboarding profiles, subjects, busy slots, tasks.
# --------------------------------------------------------------------------

import sqlite3
import hashlib
from datetime import date


DB_FILE = "cadence_users.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_profile (
            user_id INTEGER PRIMARY KEY,
            student_type TEXT,
            goal TEXT,
            sleep_hours INTEGER NOT NULL DEFAULT 8,
            school_hours INTEGER NOT NULL DEFAULT 6,
            school_days INTEGER NOT NULL DEFAULT 5,
            gym INTEGER NOT NULL DEFAULT 0,
            sports INTEGER NOT NULL DEFAULT 0,
            coaching INTEGER NOT NULL DEFAULT 0,
            commute INTEGER NOT NULL DEFAULT 0,
            part_time INTEGER NOT NULL DEFAULT 0,
            family INTEGER NOT NULL DEFAULT 0,
            extracurricular INTEGER NOT NULL DEFAULT 0,
            weekend_enabled INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS busy_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            label TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            subject TEXT,
            duration INTEGER NOT NULL,
            priority TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            start_date TEXT,
            deadline TEXT,
            is_weekend INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name: str, email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(password)
        clean_email = email.lower().strip()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name.strip(), clean_email, hashed)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists. Try signing in instead."
    finally:
        conn.close()


def verify_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    clean_email = email.lower().strip()
    cursor.execute(
        "SELECT id, name, email FROM users WHERE email = ? AND password_hash = ?",
        (clean_email, hashed)
    )
    user = cursor.fetchone()
    conn.close()
    return tuple(user) if user else None


def email_exists(email: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email.lower().strip(),))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# --------------------------------------------------------------------------
# Onboarding persistence
# --------------------------------------------------------------------------

def save_onboarding_profile(user_id: int, onboarding: dict):
    routine = onboarding.get("routine", {})

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO onboarding_profile (
            user_id, student_type, goal,
            sleep_hours, school_hours, school_days,
            gym, sports, coaching, commute, part_time, family, extracurricular, weekend_enabled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            student_type = excluded.student_type,
            goal = excluded.goal,
            sleep_hours = excluded.sleep_hours,
            school_hours = excluded.school_hours,
            school_days = excluded.school_days,
            gym = excluded.gym,
            sports = excluded.sports,
            coaching = excluded.coaching,
            commute = excluded.commute,
            part_time = excluded.part_time,
            family = excluded.family,
            extracurricular = excluded.extracurricular,
            weekend_enabled = excluded.weekend_enabled
    """, (
        user_id,
        onboarding.get("student_type"),
        onboarding.get("goal"),
        routine.get("sleep_hours", 8),
        routine.get("school_hours", 6),
        routine.get("school_days", 5),
        int(bool(routine.get("gym", False))),
        int(bool(routine.get("sports", False))),
        int(bool(routine.get("coaching", False))),
        int(bool(routine.get("commute", False))),
        int(bool(routine.get("part_time", False))),
        int(bool(routine.get("family", False))),
        int(bool(routine.get("extracurricular", False))),
        int(bool(routine.get("weekend_enabled", True))),
    ))
    conn.commit()
    conn.close()


def get_onboarding_profile(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM onboarding_profile WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def has_completed_onboarding(user_id: int) -> bool:
    return get_onboarding_profile(user_id) is not None


# --------------------------------------------------------------------------
# Subjects persistence
# --------------------------------------------------------------------------

def add_subject(user_id: int, name: str):
    name = name.strip()
    if not name:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (user_id, name) VALUES (?, ?)",
        (user_id, name)
    )
    conn.commit()
    conn.close()


def get_subjects(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM subjects WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_subject(subject_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()


def delete_all_subjects(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# Busy Slots persistence
# --------------------------------------------------------------------------

def add_busy_slot(user_id: int, day_of_week: int, start_time: str, end_time: str, label: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO busy_slots (user_id, day_of_week, start_time, end_time, label) VALUES (?, ?, ?, ?, ?)",
        (user_id, day_of_week, start_time, end_time, label.strip())
    )
    conn.commit()
    conn.close()


def get_busy_slots(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, day_of_week, start_time, end_time, label FROM busy_slots WHERE user_id = ? ORDER BY day_of_week, start_time",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_busy_slot(slot_id: int, day_of_week: int, start_time: str, end_time: str, label: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE busy_slots SET day_of_week = ?, start_time = ?, end_time = ?, label = ? WHERE id = ?",
        (day_of_week, start_time, end_time, label.strip(), slot_id)
    )
    conn.commit()
    conn.close()


def delete_busy_slot(slot_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM busy_slots WHERE id = ?", (slot_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# Tasks persistence
# --------------------------------------------------------------------------

def _date_to_str(d):
    return d.isoformat() if isinstance(d, date) else d


def _str_to_date(s):
    if isinstance(s, date):
        return s
    if s:
        try:
            return date.fromisoformat(s)
        except Exception:
            pass
    return None


def create_task(user_id: int, task: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (user_id, name, subject, duration, priority, completed, start_date, deadline, is_weekend)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        task["name"],
        task.get("subject", ""),
        task["duration"],
        task.get("priority", "Medium"),
        int(bool(task.get("completed", False))),
        _date_to_str(task.get("start_date")),
        _date_to_str(task.get("deadline")),
        int(bool(task.get("is_weekend", False))),
    ))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def get_tasks(user_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, subject, duration, priority, completed, start_date, deadline, is_weekend FROM tasks WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "subject": row["subject"],
            "duration": row["duration"],
            "priority": row["priority"],
            "completed": bool(row["completed"]),
            "start_date": _str_to_date(row["start_date"]),
            "deadline": _str_to_date(row["deadline"]),
            "is_weekend": bool(row["is_weekend"]),
        }
        for row in rows
    ]


def update_task(task: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks SET
            name = ?, subject = ?, duration = ?, priority = ?, completed = ?,
            start_date = ?, deadline = ?, is_weekend = ?
        WHERE id = ?
    """, (
        task["name"],
        task.get("subject", ""),
        task["duration"],
        task.get("priority", "Medium"),
        int(bool(task.get("completed", False))),
        _date_to_str(task.get("start_date")),
        _date_to_str(task.get("deadline")),
        int(bool(task.get("is_weekend", False))),
        task["id"],
    ))
    conn.commit()
    conn.close()


def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_user_name(user_id: int, name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user_id))
    conn.commit()
    conn.close()


def update_user_password(user_id: int, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
    conn.commit()
    conn.close()


def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return tuple(user) if user else None
