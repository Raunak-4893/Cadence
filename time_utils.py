from datetime import date, datetime, timedelta, timezone


def get_today() -> date:
    """Returns today's date from the system clock."""
    return date.today()


def get_now() -> datetime:
    """Returns current local time from the system clock."""
    return datetime.now()


def get_now_utc() -> datetime:
    """Returns current UTC time from the system clock."""
    return datetime.now(timezone.utc)


def get_tomorrow() -> date:
    """Returns tomorrow's date from the system clock."""
    return get_today() + timedelta(days=1)


def get_next_saturday() -> date:
    """Returns the upcoming Saturday, or today if today is Saturday/Sunday."""
    today = get_today()
    wd = today.weekday()
    if wd >= 5:
        return today
    return today + timedelta(days=5 - wd)