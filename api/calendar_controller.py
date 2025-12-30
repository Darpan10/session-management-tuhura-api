# app/routers/calendar.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session as DB
from datetime import datetime
from dependencies.db_dependency import get_db
from models.session import Session
from fastapi.responses import JSONResponse, Response
from utils.ical_utils import build_ics_from_session
from utils.jwt_utils import get_current_user

calendar_router = APIRouter()


# @calendar_router.get("/download/{session_id}")
# def download_calendar(session_id: int,
#                       db: DB = Depends(get_db)
#                       # current_user: dict = Depends(get_current_user)
#                       ):
#     # Fetch the session
#     session = db.query(Session).filter(Session.id == session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found")
#
#     # Build the ICS using a helper
#     ical_data = build_ics_from_session(session)
#
#     return Response(
#         content=ical_data,
#         media_type="text/calendar",
#         headers={
#             "Content-Disposition": f"attachment; filename=session_{session.title}.ics"
#         },
#     )



@calendar_router.get("/subscribe/{session_id}")
def get_subscription_url(session_id: int,
                         # current_user: dict = Depends(get_current_user)
                         request : Request,
                         db: Session = Depends(get_db)):
    """
    Returns a single subscription URL for a session.
    This URL can be added to Google Calendar.
    The ICS content is generated dynamically when Google Calendar polls it.
    """
    # Ensure session exists
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    base_url = str(request.base_url).rstrip("/")
    subscribe_url = f"{base_url}/api/calendar/{session_id}.ics"

    return JSONResponse(
        content={
            "session_id": session_id,
            "subscribe_url": subscribe_url,
        }
    )

#can be used for download
@calendar_router.get("/{session_id}.ics")
def serve_dynamic_ics(session_id: int,
                      # current_user: dict = Depends(get_current_user)
                      db: Session = Depends(get_db)):
    """
    Serve the dynamic ICS content.
    Google Calendar polls this URL to get the latest events.
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    ics_content = build_ics_from_session(session)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'inline; filename="session-{session_id}.ics"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
