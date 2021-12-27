from datetime import datetime, timedelta


def convert_hours_mins(minutes: int) -> (int, int):
    """Convert minutes into hours and minutes"""
    return int(minutes // 60), int(minutes % 60)


def time_str(minutes: int) -> str:
    hours, minutes = convert_hours_mins(minutes)
    if hours and minutes:
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"
    elif hours:
        return f"{hours}h"
    elif minutes:
        return f"{minutes}m"
    else:
        return ""


def today_str():
    return datetime.today().strftime("%Y-%m-%d")


def week_str(n=0):
    date = datetime.today() + timedelta(weeks=n)
    return date.strftime("%Y-W%W")


def week_endpoints(date: datetime) -> (str, str):
    start = date - timedelta(weeks=date.weekday())
    end = date + timedelta(days=(6 - date.weekday()))
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
