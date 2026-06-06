import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from dotenv import load_dotenv

from services.parser       import parse_input
from services.email_sender import send_report, build_email_body
from agent.runner          import run_agent
from models.schemas        import FullReport, EmailRequest, StatusResponse

load_dotenv()

app = FastAPI(title="MeetingIQ API", version="1.0.0")

reports_store     : dict[str, FullReport] = {}
transcripts_store : dict[str, str]        = {}

UPLOAD_DIR = "temp_uploads"
OUTPUT_DIR = "temp_outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "MeetingIQ API is running"}


@app.post("/analyse")
async def analyse(
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

        transcript = parse_input(file_path=file_path, text=text)

        if not transcript or len(transcript.strip()) < 50:
            raise HTTPException(status_code=400, detail="Transcript too short to analyse")

        report_id, report = run_agent(transcript)

        reports_store[report_id]     = report
        transcripts_store[report_id] = transcript

        return {
            "report_id"  : report_id,
            "report"     : report.model_dump(),
            "transcript" : transcript
        }

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


@app.get("/report/{report_id}")
def get_report(report_id: str):
    if report_id not in reports_store:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "report_id"  : report_id,
        "report"     : reports_store[report_id].model_dump(),
        "transcript" : transcripts_store.get(report_id, "")
    }


@app.get("/download/pdf/{report_id}")
def download_pdf(report_id: str):
    if report_id not in reports_store:
        raise HTTPException(status_code=404, detail="Report not found")

    from services.pdf_generator import generate_pdf
    report   = reports_store[report_id]
    pdf_path = os.path.join(OUTPUT_DIR, f"{report_id}.pdf")
    generate_pdf(report, pdf_path)

    return FileResponse(
        path       = pdf_path,
        filename   = "MeetingIQ_Report.pdf",
        media_type = "application/pdf"
    )


@app.get("/download/ppt/{report_id}")
def download_ppt(report_id: str):
    if report_id not in reports_store:
        raise HTTPException(status_code=404, detail="Report not found")

    from services.ppt_generator import generate_ppt
    report   = reports_store[report_id]
    ppt_path = os.path.join(OUTPUT_DIR, f"{report_id}.pptx")
    generate_ppt(report, ppt_path)

    return FileResponse(
        path       = ppt_path,
        filename   = "MeetingIQ_Report.pptx",
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


# ── ENDPOINT 5 — Send email (PDF + PPT both attached) ─────────────────────────
@app.post("/send-email", response_model=StatusResponse)
def send_email(request: EmailRequest):
    if request.report_id not in reports_store:
        raise HTTPException(status_code=404, detail="Report not found")

    report = reports_store[request.report_id]

    from services.pdf_generator import generate_pdf
    from services.ppt_generator import generate_ppt

    pdf_path = os.path.join(OUTPUT_DIR, f"{request.report_id}.pdf")
    ppt_path = os.path.join(OUTPUT_DIR, f"{request.report_id}.pptx")

    generate_pdf(report, pdf_path)
    generate_ppt(report, ppt_path)

    body = build_email_body(report)

    result = send_report(
        to_emails   = request.emails,
        subject     = f"Meeting Summary — {report.summary.meeting_type} | {report.summary.one_line[:60]}",
        body        = body,
        attachments = [pdf_path, ppt_path]
    )

    if result["success"]:
        return StatusResponse(
            status  = "success",
            message = f"Report sent to {len(request.emails)} recipients with PDF + PPT attached"
        )
    else:
        raise HTTPException(status_code=500, detail=result["error"])