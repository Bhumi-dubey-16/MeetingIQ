import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from typing import Optional
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.parser       import parse_input
from services.email_sender import send_report, build_email_body
from agent.runner          import run_agent
from models.schemas        import FullReport, EmailRequest, StatusResponse
from database              import init_db, save_report, get_report as db_get_report, get_recent_reports

load_dotenv()

# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app     = FastAPI(title="MeetingIQ API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Init database on startup ───────────────────────────────────────────────────
# Creates the reports table if it doesn't exist yet.
# Safe to call every time — won't overwrite existing data.
init_db()

OUTPUT_DIR = "temp_outputs"
UPLOAD_DIR = "temp_uploads"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "MeetingIQ API is running"}


@app.post("/analyse")
@limiter.limit("5/minute")
async def analyse(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: Optional[str]        = Form(None)
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either a file or text input")

    file_path = None

    try:
        if file:
            file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        try:
            transcript = parse_input(file_path=file_path, text=text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not transcript or len(transcript.strip()) < 50:
            raise HTTPException(status_code=400, detail="Transcript too short to analyse — need at least 50 characters")

        report_id, report = run_agent(transcript)

        # ── Persist to database ────────────────────────────────────────────────
        # Now survives server restarts — report_id stays valid forever
        save_report(
            report_id   = report_id,
            transcript  = transcript,
            report_dict = report.model_dump()
        )

        return {
            "report_id"  : report_id,
            "report"     : report.model_dump(),
            "transcript" : transcript
        }

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


@app.get("/report/{report_id}")
@limiter.limit("30/minute")
def get_report(request: Request, report_id: str):
    # Now reads from DB instead of in-memory dict
    data = db_get_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    return data


@app.get("/reports")
@limiter.limit("20/minute")
def list_reports(request: Request, limit: int = 20):
    """Returns the most recent N reports — useful for a dashboard."""
    return get_recent_reports(limit=limit)


@app.get("/download/pdf/{report_id}")
@limiter.limit("10/minute")
def download_pdf(request: Request, report_id: str):
    data = db_get_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")

    from services.pdf_generator import generate_pdf
    from models.schemas import FullReport

    report   = FullReport(**data["report"])
    pdf_path = os.path.join(OUTPUT_DIR, f"{report_id}.pdf")
    generate_pdf(report, pdf_path)

    return FileResponse(
        path       = pdf_path,
        filename   = "MeetingIQ_Report.pdf",
        media_type = "application/pdf"
    )


@app.get("/download/ppt/{report_id}")
@limiter.limit("10/minute")
def download_ppt(request: Request, report_id: str):
    data = db_get_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")

    from services.ppt_generator import generate_ppt
    from models.schemas import FullReport

    report   = FullReport(**data["report"])
    ppt_path = os.path.join(OUTPUT_DIR, f"{report_id}.pptx")
    generate_ppt(report, ppt_path)

    return FileResponse(
        path       = ppt_path,
        filename   = "MeetingIQ_Report.pptx",
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@app.post("/send-email", response_model=StatusResponse)
@limiter.limit("3/minute")
def send_email(request: Request, email_request: EmailRequest):
    data = db_get_report(email_request.report_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")

    from services.pdf_generator import generate_pdf
    from services.ppt_generator import generate_ppt
    from models.schemas import FullReport

    report   = FullReport(**data["report"])
    pdf_path = os.path.join(OUTPUT_DIR, f"{email_request.report_id}.pdf")
    ppt_path = os.path.join(OUTPUT_DIR, f"{email_request.report_id}.pptx")

    generate_pdf(report, pdf_path)
    generate_ppt(report, ppt_path)

    body   = build_email_body(report)
    result = send_report(
        to_emails   = email_request.emails,
        subject     = f"Meeting Summary — {report.summary.meeting_type} | {report.summary.one_line[:60]}",
        body        = body,
        attachments = [pdf_path, ppt_path]
    )

    if result["success"]:
        return StatusResponse(
            status  = "success",
            message = f"Report sent to {len(email_request.emails)} recipients with PDF + PPT attached"
        )
    else:
        raise HTTPException(status_code=500, detail=result["error"])