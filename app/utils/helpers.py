from datetime import datetime, date, timedelta
from typing import Tuple


def get_date_range_for_period(period: str) -> Tuple[datetime, datetime]:
    """
    Returns (start_dt, end_dt) UTC range for a given period: 'today', 'yesterday', 'this_week', 'last_week', 'this_month'.
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    
    if period == "today":
        return today_start, now
    elif period == "yesterday":
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start - timedelta(seconds=1)
        return yesterday_start, yesterday_end
    elif period == "this_week":
        start = today_start - timedelta(days=today_start.weekday())
        return start, now
    elif period == "last_week":
        this_week_start = today_start - timedelta(days=today_start.weekday())
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(seconds=1)
        return last_week_start, last_week_end
    elif period == "this_month":
        start = datetime(now.year, now.month, 1, 0, 0, 0)
        return start, now
    else:
        # Default to 30 days
        return now - timedelta(days=30), now


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculates percentage change cleanly.
    Example: old=100, new=84 -> change = -16.0%
    """
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    change = ((new_value - old_value) / old_value) * 100.0
    return round(change, 2)
