from datetime import datetime, timedelta

DAY_MAP = {
    "MO": 0,
    "TU": 1,
    "WE": 2,
    "TH": 3,
    "FR": 4,
    "SA": 5,
    "SU": 6,
}


def correct_dtstart_for_rule(dtstart_str: str, byday: str) -> str:
    """
    If DTSTART weekday doesn't match BYDAY, move DTSTART forward
    until it matches the weekday defined in BYDAY.
    """
    dt = datetime.strptime(dtstart_str, "%Y%m%dT%H%M%S")
    target_weekday = DAY_MAP[byday]

    while dt.weekday() != target_weekday:
        dt += timedelta(days=1)

    return dt.strftime("%Y%m%dT%H%M%S")


def build_ics_from_session(session):
    dtstamp = datetime.now().strftime("%Y%m%dT%H%M%S")

    # Split the stored rrule into DTSTART + RRULE
    lines = session.rrule.split("\n")
    dtstart_line = next((l for l in lines if l.startswith("DTSTART:")), None)
    rrule_line = next((l for l in lines if l.startswith("RRULE:")), None)

    if not dtstart_line or not rrule_line:
        raise ValueError("Invalid RRULE stored in session.")

    # Extract DTSTART value
    dtstart_value = dtstart_line.replace("DTSTART:", "").strip()

    # Extract BYDAY value from RRULE (e.g. TH from BYDAY=TH)
    parts = rrule_line.split(";")
    byday_part = next((p for p in parts if p.startswith("BYDAY=")), None)
    if not byday_part:
        raise ValueError("RRULE missing BYDAY")

    byday = byday_part.replace("BYDAY=", "")

    # AUTO-FIX DTSTART if weekday mismatch
    corrected_dtstart = correct_dtstart_for_rule(dtstart_value, byday)

    # Rebuild rrule string with corrected DTSTART
    corrected_rrule_block = (
            f"DTSTART:{corrected_dtstart}\n" +
            rrule_line
    )

    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your App Name//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:session-{session.id}@yourapp.com
DTSTAMP:{dtstamp}
{corrected_rrule_block}
SUMMARY:{session.title}
DESCRIPTION:Term {session.term} - Weekly Class
LOCATION:{session.location}, {session.city}
END:VEVENT
END:VCALENDAR
"""

    return ical
