from datetime import datetime, timezone

def generate_ical():
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//FastAPI POC//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:poc-event-123@example.com
DTSTAMP:{dtstamp}
DTSTART:20250101T100000
DTEND:20250101T110000
SUMMARY:POC Recurring Event
DESCRIPTION:This is a POC event with static RRULE
RRULE:FREQ=WEEKLY;BYDAY=MO,WE;COUNT=10
END:VEVENT
END:VCALENDAR
"""
    return ical_content
