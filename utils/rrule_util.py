from datetime import datetime

DAY_MAP = {
    "Monday": "MO",
    "Tuesday": "TU",
    "Wednesday": "WE",
    "Thursday": "TH",
    "Friday": "FR",
    "Saturday": "SA",
    "Sunday": "SU",
}

# sample rrule :
# DTSTART:20251228T153000
# RRULE:FREQ=WEEKLY;BYDAY=TH;UNTIL=20260102T173000
def generate_rrule(start_date, end_date, start_time, end_time, day_of_week):
    """
    Generate RRULE for weekly recurring session on ONE fixed weekday.
    Times are kept exactly as provided (no timezone conversion).
    """

    if day_of_week not in DAY_MAP:
        raise ValueError("Invalid day_of_week, expected 'Monday', 'Tuesday', etc.")

    byday = DAY_MAP[day_of_week]

    dtstart = datetime.combine(start_date, start_time)
    until_dt = datetime.combine(end_date, end_time)

    rrule = (
        f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\n"
        f"RRULE:FREQ=WEEKLY;BYDAY={byday};UNTIL={until_dt.strftime('%Y%m%dT%H%M%S')}"
    )

    return rrule
