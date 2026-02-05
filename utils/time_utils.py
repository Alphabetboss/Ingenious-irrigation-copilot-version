from datetime import datetime, time as dtime


def parse_hhmm(value: str) -> dtime:
    """
    Parse a HH:MM string into a datetime.time object.
    """
    hour, minute = value.split(":")
    return dtime(hour=int(hour), minute=int(minute))


def is_time_in_past_today(target: dtime, now: datetime) -> bool:
    """
    Return True if the given time today is in the past relative to 'now'.
    """
    target_dt = now.replace(hour=target.hour, minute=target.minute, second=0, microsecond=0)
    return target_dt <= now

