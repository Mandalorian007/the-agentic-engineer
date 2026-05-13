"""Shared date calculation for publishing schedule."""

import calendar
from datetime import datetime, timedelta
from typing import Dict, Any

# Map day names to weekday numbers (Python's datetime convention)
DAY_MAP = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}


def get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> int:
    """
    Find the nth occurrence of a weekday in a given month.

    Args:
        year: Calendar year
        month: Calendar month (1-12)
        weekday: Weekday number (0=Monday, 6=Sunday)
        n: Which occurrence (1=first, 2=second, etc.)

    Returns:
        Day of month for the nth occurrence

    Raises:
        ValueError: If the nth occurrence doesn't exist in the month
    """
    _, days_in_month = calendar.monthrange(year, month)
    count = 0
    for day in range(1, days_in_month + 1):
        if calendar.weekday(year, month, day) == weekday:
            count += 1
            if count == n:
                return day
    raise ValueError(
        f"No {n}th occurrence of weekday {weekday} in {year}-{month:02d}"
    )


def _parse_publish_time(publish_time: str) -> tuple:
    """Parse HH:MM:SS time string into (hour, minute, second)."""
    parts = publish_time.split(':')
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    second = int(parts[2]) if len(parts) > 2 else 0
    return hour, minute, second


def get_next_publish_date(after_date: datetime, pub_config: Dict[str, Any]) -> datetime:
    """
    Get the next publish date after a given date.

    Supports both weekly and monthly frequencies.

    Args:
        after_date: Find next publish date after this date
        pub_config: Publishing config dict with keys:
            - frequency: "weekly" or "monthly"
            - time: publish time in HH:MM:SS format
            For weekly: days (list of day names)
            For monthly: day (single day name), week_of_month (int)

    Returns:
        Next available publish date as datetime
    """
    frequency = pub_config.get('frequency', 'weekly')
    publish_time = pub_config.get('time', '11:00:00')
    hour, minute, second = _parse_publish_time(publish_time)

    if frequency == 'monthly':
        return _next_monthly_date(after_date, pub_config, hour, minute, second)
    else:
        return _next_weekly_date(after_date, pub_config, hour, minute, second)


def _next_weekly_date(after_date: datetime, pub_config: Dict[str, Any],
                      hour: int, minute: int, second: int) -> datetime:
    """Find next weekly publish date."""
    publish_days = pub_config.get('days', ['monday'])
    target_weekdays = sorted(DAY_MAP[day.lower()] for day in publish_days)

    current_date = after_date + timedelta(days=1)
    current_date = current_date.replace(
        hour=hour, minute=minute, second=second, microsecond=0
    )

    for _ in range(7):
        if current_date.weekday() in target_weekdays:
            return current_date
        current_date += timedelta(days=1)

    raise ValueError(f"Could not find next publish date. Check days: {publish_days}")


def _next_monthly_date(after_date: datetime, pub_config: Dict[str, Any],
                       hour: int, minute: int, second: int) -> datetime:
    """Find next monthly publish date (nth weekday of month).

    Supports multiple `weeks_of_month` entries (e.g. [1, 3] for bi-weekly on
    1st and 3rd Mondays). Comparison is by calendar date, so a candidate
    falling on the same calendar day as `after_date` is treated as already
    used and skipped (mirrors the weekly path which starts from after+1day).
    """
    day_name = pub_config.get('day', 'monday')
    weeks_of_month = pub_config.get('weeks_of_month', [2])
    weekday = DAY_MAP[day_name.lower()]

    year = after_date.year
    month = after_date.month
    after_calendar_date = after_date.date()

    # Check up to 13 months ahead
    for _ in range(13):
        month_candidates = []
        for week_n in weeks_of_month:
            try:
                target_day = get_nth_weekday_of_month(year, month, weekday, week_n)
                candidate = datetime(year, month, target_day, hour, minute, second)
                if candidate.date() > after_calendar_date:
                    month_candidates.append(candidate)
            except ValueError:
                continue

        if month_candidates:
            return min(month_candidates)

        # Advance to next month
        month += 1
        if month > 12:
            month = 1
            year += 1

    raise ValueError(
        f"Could not find next monthly publish date within 13 months. "
        f"Config: {day_name}, weeks {weeks_of_month}"
    )


def format_schedule_label(pub_config: Dict[str, Any]) -> str:
    """
    Return a human-readable label for the publishing schedule.

    Examples:
        "Monday" (weekly)
        "2nd Monday of each month" (monthly, single week)
        "1st and 3rd Monday of each month" (monthly, multiple weeks)
    """
    frequency = pub_config.get('frequency', 'weekly')
    ordinal_map = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th'}

    if frequency == 'monthly':
        day_name = pub_config.get('day', 'monday').capitalize()
        weeks = pub_config.get('weeks_of_month', [2])
        ordinals = [ordinal_map.get(w, f'{w}th') for w in weeks]
        if len(ordinals) == 1:
            week_str = ordinals[0]
        elif len(ordinals) == 2:
            week_str = f"{ordinals[0]} and {ordinals[1]}"
        else:
            week_str = ", ".join(ordinals[:-1]) + f", and {ordinals[-1]}"
        return f"{week_str} {day_name} of each month"
    else:
        days = pub_config.get('days', ['monday'])
        return ", ".join(day.capitalize() for day in days)
